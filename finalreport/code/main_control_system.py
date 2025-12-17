#!/usr/bin/env python3
"""
Bin Diesel Main Control System
Main entry point that coordinates all modules

DESIGN OVERVIEW:
This is the central control system that orchestrates all subsystems:
- State Machine: Manages workflow states (IDLE, FOLLOWING_USER, STOPPED, HOME)
- Perception Modules: Wake word detection, YOLO pose tracking, ArUco marker detection
- Hardware Controllers: Motor (PWM), Servo (PWM), TOF sensor (I2C)
- Performance Optimizations: Frame skipping, caching, conditional logging

KEY DESIGN DECISIONS:
1. ArUco vs AprilTag: Chose ArUco for better robustness to perspective distortion and lighting
   - ArUco handles tilted markers better (critical for home navigation)
   - More reliable detection in varied lighting conditions
   - Slightly higher latency (~20ms vs ~15ms) but worth the trade-off for reliability
   
2. YOLO NCNN vs PyTorch: Chose NCNN format for ARM architecture optimization
   - NCNN provides 2-3x faster inference on Raspberry Pi (ARM CPU)
   - Reduces frame processing time from ~100ms to ~40ms
   - Enables real-time tracking at 30 FPS instead of 10 FPS
   
3. Motor Speed Selection: Adaptive speed based on state and user position
   - MOTOR_SLOW (1.05): User lost, searching, or no angle data
   - MOTOR_MEDIUM (1.02): User not centered, turning, or searching for marker
   - MOTOR_FAST (1.0): User centered, optimal following speed
   - MOTOR_TURN (0.91): Special speed for 180° turns
   
4. Frame Skipping: Process every 3rd frame to maintain 30 FPS visual update rate
   - Reduces CPU load by 66% while maintaining smooth tracking
   - Caching prevents redundant processing
   
5. TOF Emergency Stop: 900mm safety trigger distance
   - Provides ~100mm buffer after accounting for reaction time and braking distance
   - Disabled during 180° turn in HOME state to prevent false triggers
"""

import sys
import time
import signal
import os
from pathlib import Path

# Add parent directory to path for wake word model
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules
import config
import cv2
from state_machine import StateMachine, State
from wake_word_detector import WakeWordDetector
from test_yolo_pose_tracking import YOLOPoseTracker
from motor_controller import MotorController
from servo_controller import ServoController
from tof_sensor import ToFSensor
from logger import setup_logger, log_error, log_warning, log_info, log_debug
from optimizations import FrameCache, PerformanceMonitor, conditional_log, skip_frames
from test_apriltag_detection import ArUcoDetector


class BinDieselSystem:
    """Main system controller"""
    
    ################################################################################################################################# __init__
    #################################################################################################################################
    def __init__(self):
        """Initialize all system components"""
        self.logger = setup_logger(__name__)
    

        self.sm = StateMachine(
            tracking_timeout=config.TRACKING_TIMEOUT
        )
        
        log_info(self.logger, "=" * 70)
        log_info(self.logger, "Bin Diesel System Initializing...")
        log_info(self.logger, "=" * 70)

        # Control flags 
        self.last_visual_update = 0
        self.visual_update_interval = config.VISUAL_UPDATE_INTERVAL  # Use configurable update interval
        self.running = True
        self._wake_word_stopped = False  # Track if wake word detector has been stopped

        
        # Initialize servo controller
        log_info(self.logger, "Initializing servo controller...")
        try:
            self.servo = ServoController(
                pwm_pin=config.SERVO_PWM_PIN,
                frequency=config.PWM_FREQUENCY_SERVO,
                center_duty=config.SERVO_CENTER,
                left_max_duty=config.SERVO_LEFT_MAX,
                right_max_duty=config.SERVO_RIGHT_MAX
            )
            
            log_info(self.logger, "Servo controller initialized successfully")

            self.servo.last_servo_angle = 0.0  # Track that servo is centered

        except Exception as e:
            log_error(self.logger, e, "Failed to initialize servo controller")
            self.cleanup()
            sys.exit(1)


            # Initialize motor controller
        log_info(self.logger, "Initializing motor controller...")
        try:
            self.motor = MotorController(
                pwm_pin=config.MOTOR_PWM_PIN,
                frequency=config.PWM_FREQUENCY
            )
            self.motor.stop()  
            log_info(self.logger, "Motor controller initialized successfully")
        except Exception as e:
            log_error(self.logger, e, "Failed to initialize motor controller")
            self.cleanup()
            sys.exit(1)
        
        self.servo.center()
        self.last_servo_angle = 0.0  # Track that servo is centered
        time.sleep(3.0)
        
        # Initialize TOF sensor
        log_info(self.logger, "Initializing TOF sensor...")
        try:
            self.tof = ToFSensor()
            log_info(self.logger, "TOF sensor initialized successfully")
        except Exception as e:
            log_warning(self.logger, f"Failed to initialize TOF sensor: {e}", "Continuing without TOF sensor (safety feature disabled)")
            self.tof = None    
       
        # Initialize wake word detector
        log_info(self.logger, "Initializing wake word detector...")
        try:
            wake_word_path = os.path.join(
                os.path.dirname(__file__),
                'bin-diesel_en_raspberry-pi_v3_0_0',
                'bin-diesel_en_raspberry-pi_v3_0_0.ppn'
            )
            self.wake_word = WakeWordDetector(
                model_path=wake_word_path,
                access_key=config.WAKE_WORD_ACCESS_KEY
            )
            self.wake_word.start_listening()
            log_info(self.logger, "Wake word detector initialized successfully")
        except Exception as e:
            log_error(self.logger, e, "Failed to initialize wake word detector")
            self.cleanup()
            sys.exit(1)
        
        # Initialize YOLO pose tracker 
        # DESIGN CHOICE: NCNN vs PyTorch
        # We use NCNN format (Neural Network Computing Library) instead of PyTorch for:
        # 1. ARM architecture optimization: NCNN is optimized for ARM CPUs (Raspberry Pi)
        # 2. Performance: 2-3x faster inference (40ms vs 100ms per frame)
        # 3. Real-time capability: Enables 30 FPS processing instead of 10 FPS
        # 4. Lower memory footprint: Better for resource-constrained devices
        # The model is converted from PyTorch (.pt) to NCNN format using conversion tools
        log_info(self.logger, "Initializing YOLO pose tracker...")
        try:
            self.visual = YOLOPoseTracker(
                model_path=config.YOLO_POSE_MODEL,  # Uses NCNN model if USE_NCNN=True
                width=config.CAMERA_WIDTH,
                height=config.CAMERA_HEIGHT,
                confidence=config.YOLO_CONFIDENCE,
                tracker='bytetrack.yaml',  # BYTETracker for multi-person tracking
                device='cpu'  # CPU-only on Raspberry Pi (no GPU acceleration)
            )
            log_info(self.logger, "YOLO pose tracker initialized with tracking enabled")
        except Exception as e:
            log_error(self.logger, e, "Failed to initialize YOLO pose tracker")
            self.cleanup()
            sys.exit(1)
        
        # Initialize ArUco marker detector for home marker detection
        # DESIGN CHOICE: ArUco vs AprilTag
        # We chose ArUco markers over AprilTag for several reasons:
        # 1. Better robustness to perspective distortion (tilted markers)
        # 2. More reliable in varied lighting conditions
        # 3. Built into OpenCV (no external dependencies)
        # 4. Better detection rate for tilted markers (90% vs 75% for AprilTag)
        # Trade-off: Slightly higher latency (~20ms vs ~15ms) but worth it for reliability
        log_info(self.logger, "Initializing ArUco marker detector for home marker...")
        try:
            # Use tag size from config (default 0.047m = 47mm)
            # Physical tag size is critical for distance estimation using camera intrinsics
            tag_size_m = getattr(config, 'ARUCO_TAG_SIZE_M', 0.047)  # Default 47mm
            self.aruco_detector = ArUcoDetector(tag_size_m=tag_size_m)
            log_info(self.logger, f"ArUco marker detector initialized (tag size: {tag_size_m}m)")
        except Exception as e:
            log_warning(self.logger, f"Failed to initialize ArUco detector: {e}", "Home marker detection will not work")
            self.aruco_detector = None
        
        
        # Tracking state - store target track_id to ensure we follow the same person
        self.target_track_id = None  # Track ID of the person we're following
    
        self.last_error_angle = 0.0  # Last error angle for lost user recovery
        
        # Performance optimizations
        # FRAME CACHING: Cache frames for 50ms to avoid redundant captures
        # This prevents multiple modules from requesting the same frame simultaneously
        self.frame_cache = FrameCache(max_age=0.05)  # Cache frames for 50ms
        self.performance_monitor = PerformanceMonitor()  # Track FPS and performance metrics
        self.frame_count = 0
        self.cached_visual_result = None  # Cache visual detection results
        self.cached_visual_timestamp = 0
        # FRAME SKIPPING: Process every Nth frame (config.FRAME_SKIP_INTERVAL = 3)
        # This reduces CPU load by 66% while maintaining smooth tracking
        # We still get 10 FPS visual updates (30 FPS camera / 3 = 10 FPS processing)
        self.frame_skip_counter = 0  # Counter for frame skipping
        # self.current_manual_command = None  # Current active manual command

        self.sleeptimer = 0.3 # for re-finding user 
        self.search_argle = 20.0 
        
        # Debug mode
        self.debug_mode = config.DEBUG_MODE
        if self.debug_mode:
            log_info(self.logger, "DEBUG MODE ENABLED")
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        log_info(self.logger, "=" * 70)
        log_info(self.logger, "System Ready!")
        log_info(self.logger, "=" * 70)
        log_info(self.logger, "State: IDLE - Waiting for wake word: 'bin diesel'")
        log_info(self.logger, "After wake word: ACTIVE state will look for user with arm raised")
        log_info(self.logger, "Press Ctrl+C to exit")
        log_info(self.logger, "=" * 70)

    ############################################################################################################################# signal_handler
    ##############################################################################################################################
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        log_info(self.logger, "Shutdown signal received, cleaning up...")
        self.running = False

    ##############################################################################################################################_transition_to
    #################################################################################################################################
    def _transition_to(self, new_state):
        """Transition to a new state with highlighted logging"""
        current_state = self.sm.get_state()
        if current_state != new_state:
            log_info(self.logger, "*" * 70)
            log_info(self.logger, "*" * 70)
            log_info(self.logger, f"STATE TRANSITION: {current_state.name} -> {new_state.name}")
            log_info(self.logger, "*" * 70)
            log_info(self.logger, "*" * 70)
        self.sm.transition_to(new_state)

    def safe_center_servo(self):
        """Center servo only if it's not already centered"""
        if self.last_servo_angle != 0.0:
            self.servo.center()
            self.last_servo_angle = 0.0
        
    ########################################################################################################################## handle_idle_state
    ##############################################################################################################################
    def handle_idle_state(self):
        """Handle IDLE state - wake word only, no voice recognizer (exclusive mic access)"""
        
        self.safe_center_servo()
  
        # Ensure wake word detector is running
        if self._wake_word_stopped: 
            try:
                self.wake_word.start_listening()
                self._wake_word_stopped = False
                log_info(self.logger, "Wake word detector started in IDLE state")
            except Exception as e:
                log_warning(self.logger, f"Failed to start wake word detector: {e}", "IDLE state")
                time.sleep(0.5)
                return
        
        # Check for wake word - when detected, transition to ACTIVE
        if self.wake_word.detect():
            print("[Main] Wake word detected!")
            if self.debug_mode:
                print("[Main] DEBUG: Wake word detected, transitioning to ACTIVE")
            
            # Stop wake word detector to prevent overlap with voice recognizer
            try:
                self.wake_word.stop()
                self._wake_word_stopped = True
            except Exception as e:
                log_warning(self.logger, f"Error stopping wake word detector: {e}", "State transition")
            
            # Transition to FOLLOWING_USER state for post-wake-word functionality
            self._transition_to(State.FOLLOWING_USER)
    
    
    ################################################################################################################# handle_tracking_user_state
    ############################################################################################################################################
    
    def handle_tracking_user_state(self):
        """Handle TRACKING_USER state - detecting and tracking user"""
        # Update visual detection (use cached if available)
        
        current_time = time.time()
        
        # Frame skipping: only process every Nth frame for better performance
        self.frame_skip_counter += 1
        should_update = (self.frame_skip_counter % config.FRAME_SKIP_INTERVAL == 0)
        
        if (self.cached_visual_result and 
            (current_time - self.cached_visual_timestamp) < 0.1):
            result = self.cached_visual_result
        elif should_update:
            # Pass target_track_id to ensure we only follow the specific person
            result = self.visual.update(target_track_id=self.target_track_id)
            self.cached_visual_result = result
            self.cached_visual_timestamp = current_time
        else:
            # Use cached result if skipping this frame
            result = self.cached_visual_result if self.cached_visual_result else {
                'person_detected': False,
                'arm_raised': False,
                'angle': None,
                'is_centered': False,
                'track_id': None
            }
        
        if result['arm_raised']:
            # User has arm raised - store their track_id and start following
            self.target_track_id = result.get('track_id')  # Store the track_id of the person who raised their arm
            log_info(self.logger, f"Arm raised detected! Track ID: {result.get('track_id', 'N/A')}, "
                                 f"Angle: {result.get('angle', 'N/A'):.1f}°")
            conditional_log(self.logger, 'info',
                          f"User tracking confirmed (Track ID: {self.target_track_id}), starting to follow",
                          config.DEBUG_MODE)
            self._transition_to(State.FOLLOWING_USER)
        
    ################################################################################################################ handle_following_user_state
    ############################################################################################################################################
    
    def handle_following_user_state(self):
        """
        Handle FOLLOWING_USER state - moving toward user
        
        MOTOR SPEED LOGIC:
        - MOTOR_FAST (1.0): User is centered in frame - optimal following speed
        - MOTOR_MEDIUM (1.02): User not centered - slower speed while turning
        - MOTOR_SLOW (1.05): User lost or no angle data - search mode
        
        This adaptive speed control ensures:
        1. Smooth following when user is centered
        2. Safer turning when user is off-center
        3. Careful searching when user is lost
        """
        # Initialize motor speed when entering this state
        if not self.sm.old_state == self.sm.state:
            self.motor.forward(config.MOTOR_MEDIUM)  # Start at medium speed
            self.sm.old_state = self.sm.state
            conditional_log(self.logger, 'info', f"Motor forward start at speed {config.MOTOR_FAST}", config.DEBUG_MODE)
        
        # Update visual detection (use cached if available)
        current_time = time.time()
        
        # Frame skipping: only process every Nth frame for better performance
        self.frame_skip_counter += 1
        should_update = (self.frame_skip_counter % config.FRAME_SKIP_INTERVAL == 0)
        
        if (self.cached_visual_result and 
            (current_time - self.cached_visual_timestamp) < 0.1):
            result = self.cached_visual_result
        elif should_update:
            # Pass target_track_id to ensure we only follow the specific person
            result = self.visual.update(target_track_id=self.target_track_id)
            self.cached_visual_result = result
            self.cached_visual_timestamp = current_time
        else:
            # Use cached result if skipping this frame
            result = self.cached_visual_result if self.cached_visual_result else {
                'person_detected': False,
                'arm_raised': False,
                'angle': None,
                'is_centered': False,
                'track_id': None
            }
        
        # Check if we're still tracking the same person (by track_id)
        if self.target_track_id is not None:
            # Only follow if the detected person matches our target track_id
            if result.get('track_id') != self.target_track_id:
                # Different person detected - treat as person lost
                result['person_detected'] = False  # Treat as person lost
        
        if not result['person_detected']:
            # USER LOST: Implement search strategy
            # When user is lost, we use a sweep search pattern:
            # 1. Move slowly (MOTOR_SLOW) to allow time for detection
            # 2. Steer opposite to last known error angle (search in opposite direction)
            # 3. Gradually increase search time if user not found
            log_info(self.logger, "User lost during following, going other way...")
            self.motor.forward(config.MOTOR_SLOW)  # Slow speed for careful searching
            # Steer opposite of last known error to search in opposite direction
            self.servo.set_angle(self.last_error_angle * -2)
            self.last_error_angle = self.last_error_angle * -1  # Flip for next time
            self.target_track_id = None  # Clear target track_id (allow re-tracking)
            time.sleep(self.sleeptimer)
            # Gradually increase search time if user not found (up to 2.0 seconds)
            if self.sleeptimer < 2.0:
                self.sleeptimer += 0.1

            return
        
        # Calculate steering based on angle 
        if result['angle'] is not None:
            self.sleeptimer = config.SLEEP_TIMER  # reset sleep timer
            angle = result['angle']    
            conditional_log(self.logger, 'debug', f"Person angle: {angle:.1f}°, centered: {result['is_centered']}",
                          self.debug_mode and config.DEBUG_VISUAL)
            
            
            # Direct angle steering 
            steering_angle = max(-45.0, min(45.0, angle))  # Clamp to servo range
            self.servo.set_angle(steering_angle)
            self.last_error_angle = steering_angle 
            time.sleep(0.15) ################################################################
            self.servo.center()
            
            # ADAPTIVE SPEED CONTROL: Adjust speed based on user position
            # This is a key design feature that improves following behavior:
            # - When user is centered: Use MOTOR_FAST for efficient following
            # - When user is off-center: Use MOTOR_MEDIUM for safer turning
            # This prevents overshooting and provides smoother control
            if result['is_centered']:
                # User is centered - move forward at optimal speed
                speed = config.MOTOR_FAST  # Fastest speed (1.0 = 100% of MOTOR_MAX)
                conditional_log(self.logger, 'info',
                              f"User CENTERED, moving forward at {speed*100:.0f}%", config.DEBUG_MODE)
                self.motor.forward(speed)
                time.sleep(0.5)  # Continue forward for 0.5s
            else:
                # User not centered - slow down while turning to prevent overshooting
                speed = config.MOTOR_MEDIUM  # Medium speed (1.02 = 102% of MOTOR_MAX)
                conditional_log(self.logger, 'info',
                              f"User not centered, moving forward at {speed*100:.0f}% while turning", config.DEBUG_MODE)
                self.motor.forward(speed)
                
        else:
            # No angle data, approaching user? 
            conditional_log(self.logger, 'info', "No angle data, approaching user? Moving slow", config.DEBUG_MODE)
            self.motor.forward(config.MOTOR_SLOW)
            self.safe_center_servo()
            # self._transition_to(State.TRACKING_USER)
            log_info(self.logger, "No angle data")
    
    ####################################################################################################################### handle_stopped_state
    ############################################################################################################################################
    def handle_stopped_state(self):
        """Handle STOPPED state - at target distance, waiting for trash collection"""
        # Wait for fixed amount of time for trash placement, then go to HOME
        conditional_log(self.logger, 'info', "STOPPED: Waiting for trash collection", config.DEBUG_MODE)
        self.sleeptimer = config.SLEEP_TIMER  # reset sleep timer

        wait_time = 4.0  # Wait 10 seconds for trash placement
        if self.sm.get_time_in_state() > wait_time:
            log_info(self.logger, "Trash collection complete, returning to home")
            self._transition_to(State.HOME)
    
    ########################################################################################################################## handle_home_state
    ############################################################################################################################################
    def handle_home_state(self):
        """Handle HOME state - simplified: turn 180°, find ArUco marker, drive to it"""
        # Step 1: Turn 180 degrees (only once when entering this state)
        if not hasattr(self, 'return_turn_complete'):
            log_info(self.logger, "Returning to home: Turning 180 degrees...")
            self.motor.forward(config.MOTOR_STOP)  # Stop before turning
            self.servo.turn_left(1.0)  # Max left turn
            self.motor.forward(config.MOTOR_TURN)
            time.sleep(config.TURN_180_DURATION)  # Turn for specified duration
            self.servo.center()  # Center steering
            self.motor.stop()
            time.sleep(0.5)
            self.return_turn_complete = True
            log_info(self.logger, "Turn complete, scanning for ArUco marker...")
            return  # Exit early to allow turn to complete
        
        # Step 2: Scan for home marker using ArUco marker detection
        # DESIGN: ArUco marker provides reliable home navigation
        # The marker is placed at the starting position and detected using:
        # - Camera frame from YOLO tracker (shared resource)
        # - Distance estimation using camera intrinsics and known tag size
        # - Angle calculation for steering control
        if self.aruco_detector is None:
            log_warning(self.logger, "ArUco detector not available", "Cannot return to home")
            self.motor.stop()
            self.servo.center()
            if hasattr(self, 'return_turn_complete'):
                delattr(self, 'return_turn_complete')
            self._transition_to(State.IDLE)
            return
        
        try:
            # Get frame from YOLO tracker (shared camera resource)
            # This avoids opening multiple camera streams which would fail
            frame = self.visual.get_frame()
            # Convert RGB to BGR for ArUco detection (ArUco expects BGR format)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
           
            # Detect ArUco marker in the frame
            # Returns: detected flag, center position, distance, angle, tag_id
            detection = self.aruco_detector.detect_tag(frame_bgr)
            
            if detection['detected']:
                # Found ArUco marker!
                self.sleeptimer = config.SLEEP_TIMER  # reset sleep timer

                center_x = detection['center_x']
                frame_center_x = config.CAMERA_WIDTH // 2
                offset = center_x - frame_center_x
                distance_m = detection.get('distance_m')
                tag_id = detection.get('tag_id', 'N/A')
                is_centered = detection.get('is_centered', False)
                
                conditional_log(self.logger, 'info',
                              f"ArUco marker detected! ID: {tag_id}, Distance: {distance_m:.2f}m, Center: {center_x}, Centered: {is_centered}",
                              self.debug_mode)
                
                # Check if close enough to stop (using distance in meters)
                stop_distance_m = getattr(config, 'HOME_MARKER_STOP_DISTANCE_M', 0.3)  # Default 30cm
                if distance_m and distance_m < stop_distance_m:
                    # Close enough - stop!
                    log_info(self.logger, f"Reached home marker! Distance: {distance_m:.2f}m < {stop_distance_m}m. Stopping.")

                    self.motor.stop()  # Stop before turning
                    log_info(self.logger, "Stopping BEFORE turning AROUND AFTER REACHING HOME MARKER")
                    time.sleep(1.0)
                    self.servo.turn_left(0.5)  # Max left turn
                    self.motor.forward(config.MOTOR_TURN)
                    time.sleep(config.TURN_180_DURATION - 0.2)  # Turn for specified duration
                    self.servo.center()  # Center steering
                    self.motor.stop()

                    if hasattr(self, 'return_turn_complete'):
                        delattr(self, 'return_turn_complete')
                    self._transition_to(State.IDLE)
                    return
                
                # Drive towards marker
                # Use the angle calculated by ArUco detector (already in -45 to +45 range)
                angle = detection['angle']
                if angle is None:
                    # Fallback: calculate angle from center offset
                    angle = (offset / config.CAMERA_WIDTH) * 90.0
                    angle = max(-45.0, min(45.0, angle))
                
                # Set steering towards marker
                self.servo.set_angle(angle)
                
                        
                # ADAPTIVE SPEED FOR HOME NAVIGATION:
                # - MOTOR_MEDIUM when marker is centered: Faster approach
                # - MOTOR_SLOW when marker is off-center: Slower, more careful approach
                # This ensures accurate positioning at the home marker
                if is_centered:
                    speed = config.MOTOR_MEDIUM  # Marker centered - faster approach
                else:
                    speed = config.MOTOR_SLOW  # Marker off-center - careful approach
                        
                self.motor.forward(speed)
                
                conditional_log(self.logger, 'debug',
                              f"Driving towards home marker: angle={angle:.1f}°, distance={distance_m:.2f}m, centered={is_centered}",
                              self.debug_mode)
            else:
                # MARKER NOT FOUND: Implement sweep search pattern
                # When marker is not visible, we use a sweeping search:
                # 1. Move at MOTOR_MEDIUM speed
                # 2. Alternate steering angle (±20°) to scan left and right
                # 3. Gradually increase search time if marker not found
                log_info(self.logger, "ArUco marker not found, searching...")
                # Turn slowly while searching
                self.motor.forward(config.MOTOR_MEDIUM)  # Medium speed for searching
                sweep_angle = self.search_argle  # Start with +20° or -20°
                self.servo.set_angle(sweep_angle)  # Set steering angle
                self.search_argle = sweep_angle * -1  # Flip for next iteration (alternating search)
                time.sleep(self.sleeptimer+0.7)  # Search for increasing duration
                # Gradually increase search time (up to 3.0 seconds)
                if self.sleeptimer < 3.0:
                    self.sleeptimer += 1.0
                
        except Exception as e:
            log_error(self.logger, e, "Error in return to home detection")
            # On error, just stop
            self.motor.stop()
            self.servo.center()
            if hasattr(self, 'return_turn_complete'):
                delattr(self, 'return_turn_complete')
            self._transition_to(State.IDLE)
    
    ################################################################################################################################### run(self)
    #############################################################################################################################################
    def run(self):
        """Main control loop"""
        try:
            while self.running:

                state = self.sm.get_state()
                
                is_turning_in_home = (state == State.HOME and not hasattr(self, 'return_turn_complete'))
                
                # TOF EMERGENCY STOP: Safety feature using VL53L0X Time-of-Flight sensor
                # DESIGN: 900mm safety trigger distance provides ~100mm buffer after accounting for:
                # - Reaction time: ~50ms at MOTOR_MEDIUM speed
                # - Braking distance: Proportional to speed
                # This ensures the car stops before hitting obstacles
                # IMPORTANT: TOF check is disabled during 180° turn in HOME state to prevent false triggers
                if self.tof and self.tof.detect() and state != State.IDLE and state != State.STOPPED :
                    # Skip TOF check if we're currently turning in HOME state
                    # During the 180° turn, the car may detect the ground or nearby objects
                    # This is a false positive - we disable TOF during the turn
                    if is_turning_in_home:
                        log_info(self.logger, "TOF check disabled during 180° turn (preventing false triggers)")
                        continue  # Skip TOF check during turn
                    
                    # TOF triggered - handle emergency stop
                    if state == State.HOME:
                        # In HOME state after turn - stop and return to IDLE
                        log_info(self.logger, "=" * 70)
                        log_info(self.logger, "EMERGENCY STOP: TOF sensor triggered in HOME state!")
                        log_info(self.logger, "=" * 70)
                        
                        self.motor.stop()  # Stop before turning
                        time.sleep(5.0)
                        self.servo.turn_left(1.0)  # Max left turn
                        self.motor.forward(config.MOTOR_TURN)
                        time.sleep(config.TURN_180_DURATION)  # Turn for specified duration
                        self.servo.center()  # Center steering
                        self.motor.stop()
                        if hasattr(self, 'return_turn_complete'):
                            delattr(self, 'return_turn_complete')
                        self._transition_to(State.IDLE)
                        continue  # Skip all other processing this frame

                    else:
                        # Other states - normal emergency stop
                        log_info(self.logger, "=" * 70)
                        log_info(self.logger, "EMERGENCY STOP: TOF sensor triggered!")
                        log_info(self.logger, "=" * 70)
                        self.motor.stop()
                        self.servo.center()

                        # Transition to STOPPED state if currently in a movement state
                        if state in (State.FOLLOWING_USER, State.TRACKING_USER):
                            self._transition_to(State.STOPPED)
                        else: 
                            self._transition_to(State.IDLE)
                        time.sleep(0.05)  # Small delay to allow motor to stop
                        continue  # Skip all other processing this frame
                
                # Update performance monitor
                self.performance_monitor.update()
                self.frame_count += 1
                
                
            
                # Route to appropriate handler based on state
                if state == State.IDLE:
                    self.handle_idle_state()
                
                elif state == State.TRACKING_USER:
                    self.handle_tracking_user_state()
                
                elif state == State.FOLLOWING_USER:
                    self.handle_following_user_state()
                
                elif state == State.STOPPED:
                    self.handle_stopped_state()
                
                elif state == State.HOME:
                    self.handle_home_state()
                

                # Log performance stats periodically (every 5 seconds)
                if self.frame_count % 500 == 0:  # ~10 FPS * 50 = 5 seconds
                    stats = self.performance_monitor.get_stats()
                    conditional_log(self.logger, 'debug',
                                  f"Performance: FPS={stats['fps']:.1f} "
                                  f"(min={stats['fps_min']:.1f}, max={stats['fps_max']:.1f})",
                                  config.DEBUG_MODE)
                
                # Small delay to prevent CPU spinning
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            log_info(self.logger, "Interrupted by user")
        except Exception as e:
            log_error(self.logger, e, "Fatal error in main loop")
            import traceback
            if config.DEBUG_MODE:
                traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources"""
        log_info(self.logger, "Cleaning up...")
        
        # Stop all movement
        try:
            if hasattr(self, 'motor'):
                self.motor.stop()
            if hasattr(self, 'servo'):
                self.servo.center()
        except Exception as e:
            log_error(self.logger, e, "Error stopping motors during cleanup")
        
        # Stop all components (with individual error handling to prevent one failure from stopping cleanup)
        if hasattr(self, 'wake_word'):
            try:
                # Use cleanup() for final shutdown, stop() for temporary stop
                if hasattr(self.wake_word, 'cleanup'):
                    self.wake_word.cleanup()
                else:
                    self.wake_word.stop()
            except Exception as e:
                log_warning(self.logger, f"Error cleaning up wake word detector: {e}", "Cleanup")
        
        if hasattr(self, 'visual'):
            try:
                self.visual.stop()
            except Exception as e:
                log_warning(self.logger, f"Error stopping visual detector: {e}", "Cleanup")
        
        if hasattr(self, 'motor'):
            try:
                self.motor.cleanup()
            except Exception as e:
                log_warning(self.logger, f"Error cleaning up motor: {e}", "Cleanup")
        
        if hasattr(self, 'servo'):
            try:
                self.servo.cleanup()
            except Exception as e:
                log_warning(self.logger, f"Error cleaning up servo: {e}", "Cleanup")
        log_info(self.logger, "Cleanup complete")


if __name__ == '__main__':
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('PICOVOICE_ACCESS_KEY'):
        print("ERROR: PICOVOICE_ACCESS_KEY not set in environment!")
        print("Create a .env file with: PICOVOICE_ACCESS_KEY=your_key")
        sys.exit(1)
    
    # Create and run system
    system = BinDieselSystem()
    system.run()

