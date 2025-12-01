"""
Main control script for ReSpeaker direction estimation and car steering control
"""

import time
import signal
import sys
from audio_capture import ReSpeakerCapture
from direction_estimator import DirectionEstimator
from psoc_communicator import PSoCCommunicator


class DirectionControlSystem:
    """Main system controller for direction estimation and car steering"""
    
    def __init__(self, psoc_port: str = '/dev/ttyUSB0', 
                 psoc_baudrate: int = 115200,
                 sample_rate: int = 16000,
                 update_rate: float = 10.0):
        """
        Initialize the direction control system
        
        Args:
            psoc_port: Serial port for PSoC communication
            psoc_baudrate: Baud rate for PSoC communication
            sample_rate: Audio sample rate
            update_rate: Control loop update rate in Hz
        """
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        
        # Initialize components
        self.audio_capture = ReSpeakerCapture(sample_rate=sample_rate)
        self.direction_estimator = DirectionEstimator(sample_rate=sample_rate)
        self.psoc_communicator = PSoCCommunicator(port=psoc_port, baudrate=psoc_baudrate)
        
        # Angle smoothing buffer
        self.angle_history = []
        self.history_size = 10
        
        # Control state
        self.running = False
        self.last_angle = 0.0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the direction control system"""
        print("Starting Direction Control System...")
        print("=" * 50)
        
        # Start audio capture
        print("Initializing audio capture...")
        self.audio_capture.start_stream()
        time.sleep(0.5)  # Allow stream to stabilize
        
        # Connect to PSoC
        print("Connecting to PSoC...")
        if not self.psoc_communicator.connect():
            print("Warning: Could not connect to PSoC. Continuing without PSoC control.")
        
        print("\nSystem ready. Processing audio and estimating direction...")
        print("Press Ctrl+C to stop.\n")
        
        self.running = True
        self.run_control_loop()
    
    def run_control_loop(self):
        """Main control loop"""
        last_update = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Read audio chunk
            try:
                left_channel, right_channel = self.audio_capture.read_chunk()
            except Exception as e:
                print(f"Error reading audio: {e}")
                time.sleep(0.01)
                continue
            
            # Estimate direction
            angle = self.direction_estimator.estimate_angle(left_channel, right_channel)
            
            # Update angle history
            if angle is not None:
                self.angle_history.append(angle)
                if len(self.angle_history) > self.history_size:
                    self.angle_history.pop(0)
            
            # Smooth angle estimate
            smoothed_angle = self.direction_estimator.smooth_angle(self.angle_history)
            
            # Update at specified rate
            if current_time - last_update >= self.update_interval:
                if smoothed_angle is not None:
                    self.last_angle = smoothed_angle
                    # Send angle to PSoC
                    self.psoc_communicator.send_angle_simple(smoothed_angle)
                    print(f"Angle: {smoothed_angle:6.2f}° | "
                          f"Raw: {angle:6.2f}°" if angle else "Angle: N/A")
                else:
                    # Keep last valid angle or send 0
                    if self.last_angle != 0:
                        print(f"No signal detected. Last angle: {self.last_angle:.2f}°")
                
                last_update = current_time
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)
    
    def stop(self):
        """Stop the system and cleanup"""
        self.running = False
        print("\nStopping system...")
        self.audio_capture.cleanup()
        self.psoc_communicator.disconnect()
        print("System stopped.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ReSpeaker Direction Estimation and Car Steering Control'
    )
    parser.add_argument('--port', type=str, default='/dev/ttyUSB0',
                       help='Serial port for PSoC (default: /dev/ttyUSB0)')
    parser.add_argument('--baudrate', type=int, default=115200,
                       help='Serial baud rate (default: 115200)')
    parser.add_argument('--sample-rate', type=int, default=16000,
                       help='Audio sample rate (default: 16000)')
    parser.add_argument('--update-rate', type=float, default=10.0,
                       help='Control loop update rate in Hz (default: 10.0)')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available serial ports and exit')
    
    args = parser.parse_args()
    
    if args.list_ports:
        comm = PSoCCommunicator()
        comm.list_available_ports()
        return
    
    # Create and start system
    system = DirectionControlSystem(
        psoc_port=args.port,
        psoc_baudrate=args.baudrate,
        sample_rate=args.sample_rate,
        update_rate=args.update_rate
    )
    
    try:
        system.start()
    except KeyboardInterrupt:
        system.stop()


if __name__ == '__main__':
    main()

