#!/usr/bin/env python3
"""
Manual Control Mode
Voice-controlled manual car operation
- Always listening for voice commands
- Executes command until new command is issued
- Emergency stop when near objects (TOF sensor)
"""

import sys
import time
import signal
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent))

import config
from motor_controller import MotorController
from servo_controller import ServoController
from tof_sensor import ToFSensor
from voice_recognizer import VoiceRecognizer
from logger import setup_logger, log_info, log_error, log_warning

# Initialize logger
logger = setup_logger(__name__)


class ManualControl:
    """Manual voice-controlled car operation"""
    
    # Command states
    COMMAND_STOP = 'STOP'
    COMMAND_FORWARD = 'FORWARD'
    COMMAND_LEFT = 'LEFT'
    COMMAND_RIGHT = 'RIGHT'
    COMMAND_TURN_AROUND = 'TURN_AROUND'
    
    def __init__(self):
        """Initialize manual control system"""
        log_info(logger, "Initializing manual control system...")
        
        # Initialize hardware controllers
        try:
            self.motor = MotorController(
                pwm_pin=config.MOTOR_PWM_PIN,
                frequency=config.PWM_FREQUENCY_MOTOR
            )
            log_info(logger, "Motor controller initialized")
        except Exception as e:
            log_error(logger, e, "Failed to initialize motor controller")
            raise
        
        try:
            self.servo = ServoController(
                pwm_pin=config.SERVO_PWM_PIN,
                frequency=config.PWM_FREQUENCY_SERVO,
                center_duty=config.SERVO_CENTER,
                left_max_duty=config.SERVO_LEFT_MAX,
                right_max_duty=config.SERVO_RIGHT_MAX
            )
            log_info(logger, "Servo controller initialized")
        except Exception as e:
            log_error(logger, e, "Failed to initialize servo controller")
            raise
        
        try:
            self.tof = ToFSensor()
            log_info(logger, "TOF sensor initialized")
        except Exception as e:
            log_warning(logger, f"Failed to initialize TOF sensor: {e}", "Emergency stop may not work")
            self.tof = None
        
        # Initialize voice recognizer
        try:
            # Get device index from config if available (same as wake word detector)
            device_index = getattr(config, 'MICROPHONE_DEVICE_INDEX', None)
            self.voice = VoiceRecognizer(
                api_key=getattr(config, 'OPENAI_API_KEY', None),
                model="gpt-4o-mini",
                device_index=device_index
            )
            log_info(logger, "Voice recognizer initialized")
        except Exception as e:
            log_error(logger, e, "Failed to initialize voice recognizer")
            raise
        
        # Current command state
        self.current_command = self.COMMAND_STOP
        self.running = True
        
        # Emergency stop flag
        self.emergency_stopped = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        log_info(logger, "Manual control system initialized")
        log_info(logger, "Say commands: FORWARD, LEFT, RIGHT, STOP, TURN AROUND")
        log_info(logger, "Press Ctrl+C to exit")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        log_info(logger, "Shutdown signal received, stopping...")
        self.running = False
        self.stop_all()
    
    def check_emergency_stop(self):
        """Check TOF sensor for emergency stop"""
        if self.tof is None:
            return False
        
        try:
            # Check if object is too close
            obstacle_detected = self.tof.detect()
            
            if obstacle_detected:
                if not self.emergency_stopped:
                    log_warning(logger, "EMERGENCY STOP: Object detected too close!", "Stopping immediately")
                    self.emergency_stopped = True
                    self.stop_all()
                return True
            else:
                # Clear emergency stop flag when obstacle is gone
                if self.emergency_stopped:
                    log_info(logger, "Obstacle cleared, resuming operation")
                    self.emergency_stopped = False
                return False
        except Exception as e:
            log_error(logger, e, "Error checking TOF sensor")
            return False
    
    def stop_all(self):
        """Stop motor and center servo"""
        self.motor.stop()
        self.servo.center()
        self.current_command = self.COMMAND_STOP
    
    def execute_command(self, command):
        """Execute a voice command"""
        if command == self.current_command:
            # Same command - continue executing
            return
        
        log_info(logger, f"New command: {command}")
        self.current_command = command
        
        # Stop previous command
        self.motor.stop()
        self.servo.center()
        time.sleep(0.1)  # Brief pause between commands
        
        if command == self.COMMAND_STOP:
            self.stop_all()
            log_info(logger, "Stopped")
        
        elif command == self.COMMAND_FORWARD:
            self.servo.center()
            self.motor.forward(config.MOTOR_MEDIUM)
            log_info(logger, "Moving forward")
        
        elif command == self.COMMAND_LEFT:
            self.servo.turn_left(1.0)  # Full left turn
            self.motor.forward(config.MOTOR_SLOW)
            log_info(logger, "Turning left")
        
        elif command == self.COMMAND_RIGHT:
            self.servo.turn_right(1.0)  # Full right turn
            self.motor.forward(config.MOTOR_SLOW)
            log_info(logger, "Turning right")
        
        elif command == self.COMMAND_TURN_AROUND:
            # Turn 180 degrees
            log_info(logger, "Turning around...")
            self.motor.stop()
            self.servo.turn_left(1.0)  # Max left turn
            self.motor.forward(config.MOTOR_TURN)
            time.sleep(config.TURN_180_DURATION)  # Turn for specified duration
            self.servo.center()
            self.motor.stop()
            log_info(logger, "Turn around complete")
            self.current_command = self.COMMAND_STOP  # Reset to stop after turn
        
        else:
            log_warning(logger, f"Unknown command: {command}", "Ignoring")
    
    def run(self):
        """Main control loop"""
        log_info(logger, "Starting manual control loop...")
        
        # Start in stopped state
        self.stop_all()
        
        # Last command check time (for continuous execution)
        last_command_check = time.time()
        command_check_interval = 0.1  # Check for new commands every 100ms
        
        # Continuous command execution loop
        while self.running:
            try:
                # Check for emergency stop (highest priority)
                if self.check_emergency_stop():
                    # Emergency stop active - don't execute commands
                    time.sleep(0.1)
                    continue
                
                # Check for new voice command (non-blocking)
                current_time = time.time()
                if current_time - last_command_check >= command_check_interval:
                    # Try to recognize a command (with short timeout to avoid blocking)
                    command = self.voice.recognize_command(timeout=0.1)
                    
                    if command:
                        # Filter out mode-switching commands (only accept movement commands)
                        if command in [self.COMMAND_STOP, self.COMMAND_FORWARD, 
                                       self.COMMAND_LEFT, self.COMMAND_RIGHT, 
                                       self.COMMAND_TURN_AROUND]:
                            self.execute_command(command)
                            last_command_check = current_time
                        else:
                            # Mode switching command - ignore in manual mode
                            log_info(logger, f"Ignoring mode command in manual mode: {command}")
                    
                    last_command_check = current_time
                
                # Continue executing current command
                if self.current_command == self.COMMAND_FORWARD:
                    # Keep moving forward
                    if not self.emergency_stopped:
                        self.motor.forward(config.MOTOR_MEDIUM)
                        self.servo.center()
                
                elif self.current_command == self.COMMAND_LEFT:
                    # Keep turning left
                    if not self.emergency_stopped:
                        self.servo.turn_left(1.0)
                        self.motor.forward(config.MOTOR_SLOW)
                
                elif self.current_command == self.COMMAND_RIGHT:
                    # Keep turning right
                    if not self.emergency_stopped:
                        self.servo.turn_right(1.0)
                        self.motor.forward(config.MOTOR_SLOW)
                
                # Small sleep to prevent CPU spinning
                time.sleep(0.05)
            
            except KeyboardInterrupt:
                log_info(logger, "Keyboard interrupt received")
                break
            except Exception as e:
                log_error(logger, e, "Error in manual control loop")
                time.sleep(0.5)  # Brief pause before retrying
        
        # Cleanup
        log_info(logger, "Stopping manual control...")
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        log_info(logger, "Cleaning up...")
        self.stop_all()
        
        try:
            if hasattr(self, 'voice'):
                self.voice.cleanup()
        except Exception as e:
            log_error(logger, e, "Error cleaning up voice recognizer")
        
        try:
            if hasattr(self, 'motor'):
                self.motor.cleanup()
        except Exception as e:
            log_error(logger, e, "Error cleaning up motor")
        
        try:
            if hasattr(self, 'servo'):
                self.servo.cleanup()
        except Exception as e:
            log_error(logger, e, "Error cleaning up servo")
        
        log_info(logger, "Cleanup complete")


def main():
    """Main entry point"""
    print("=" * 70)
    print("Manual Control Mode")
    print("=" * 70)
    print("Voice Commands:")
    print("  - FORWARD: Move forward")
    print("  - LEFT: Turn left")
    print("  - RIGHT: Turn right")
    print("  - STOP: Stop movement")
    print("  - TURN AROUND: Turn 180 degrees")
    print()
    print("Features:")
    print("  - Always listening for commands")
    print("  - Commands execute continuously until new command issued")
    print("  - Emergency stop when object detected (TOF sensor)")
    print()
    print("Press Ctrl+C to exit")
    print("=" * 70)
    print()
    
    try:
        manual = ManualControl()
        manual.run()
    except Exception as e:
        log_error(logger, e, "Fatal error in manual control")
        sys.exit(1)


if __name__ == '__main__':
    main()

