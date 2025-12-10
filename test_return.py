#!/usr/bin/env python3
"""
Standalone Return-to-Home Test Script
Tests the return-to-home functionality:
1. Turn hard right for set duration (to turn around)
2. Detect red box using YOLO object detection + color tracking
3. Drive towards it
4. Stop when 10cm away (using TOF sensor)
"""

import sys
import time
import cv2
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from motor_controller import MotorController
from servo_controller import ServoController
from tof_sensor import ToFSensor
from test_yolo_pose_tracking import YOLOPoseTracker
from picamera2 import Picamera2

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not installed!")
    print("Install with: pip install ultralytics")
    sys.exit(1)


class ReturnToHomeTest:
    """Standalone return-to-home test"""
    
    def __init__(self):
        """Initialize all components"""
        print("=" * 70)
        print("Return-to-Home Test")
        print("=" * 70)
        
        # Initialize motor controller
        print("[TEST] Initializing motor controller...")
        self.motor = MotorController(
            pwm_pin=config.MOTOR_PWM_PIN,
            frequency=config.PWM_FREQUENCY
        )
        self.motor.stop()
        print("[TEST] Motor controller initialized")
        
        # Initialize servo controller
        print("[TEST] Initializing servo controller...")
        self.servo = ServoController(
            pwm_pin=config.SERVO_PWM_PIN,
            frequency=config.PWM_FREQUENCY,
            center_duty=config.SERVO_CENTER,
            left_max_duty=config.SERVO_LEFT_MAX,
            right_max_duty=config.SERVO_RIGHT_MAX
        )
        self.servo.center()
        print("[TEST] Servo controller initialized")
        
        # Initialize TOF sensor
        print("[TEST] Initializing TOF sensor...")
        self.tof = ToFSensor()
        print("[TEST] TOF sensor initialized")
        
        # Initialize YOLO object detection model (NCNN or PyTorch)
        print("[TEST] Initializing YOLO object detection...")
        try:
            self.yolo_model = YOLO(config.YOLO_MODEL)
            print(f"[TEST] YOLO model loaded: {config.YOLO_MODEL}")
        except Exception as e:
            # Fallback: if NCNN failed, try PyTorch
            if config.USE_NCNN and config.YOLO_MODEL.endswith('_ncnn_model'):
                fallback_path = config.YOLO_MODEL.replace('_ncnn_model', '.pt')
                print(f"[TEST] NCNN model not found, trying PyTorch: {fallback_path}")
                self.yolo_model = YOLO(fallback_path)
                print(f"[TEST] PyTorch model loaded: {fallback_path}")
            else:
                raise e
        
        # Initialize camera
        print("[TEST] Initializing camera...")
        self.picam2 = Picamera2()
        preview_config = self.picam2.create_preview_configuration(
            main={"size": (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), "format": "RGB888"},
            controls={"FrameRate": config.CAMERA_FPS}
        )
        self.picam2.configure(preview_config)
        self.picam2.start()
        time.sleep(1.5)  # Wait for camera to initialize
        print(f"[TEST] Camera started: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
        
        # Configuration
        self.turn_duration = 3.0  # Seconds to turn right (tune this to turn exactly 180°)
        self.stop_distance_mm = 100  # Stop when 10cm (100mm) away
        self.target_object_class = 'box'  # YOLO object class to detect
        self.target_color = 'red'  # Color of the box
        self.color_threshold = 0.3  # Minimum 30% of object must match color
        
        print()
        print("Configuration:")
        print(f"  Turn duration: {self.turn_duration}s")
        print(f"  Stop distance: {self.stop_distance_mm}mm (10cm)")
        print(f"  Target object: {self.target_object_class}")
        print(f"  Target color: {self.target_color}")
        print("=" * 70)
        print()
    
    def _check_color_match(self, frame, bbox, target_color):
        """
        Check if object in bounding box matches target color
        
        Args:
            frame: RGB frame
            bbox: Bounding box (x1, y1, x2, y2)
            target_color: Color name ('red', 'blue', 'green', etc.)
            
        Returns:
            float: Percentage of pixels matching color (0.0-1.0)
        """
        import numpy as np
        
        x1, y1, x2, y2 = bbox
        h, w = frame.shape[:2]
        
        # Ensure coordinates are within frame bounds
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        # Extract object region
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return 0.0
        
        # Convert RGB to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        # Define color ranges in HSV
        color_ranges = {
            'red': [
                (np.array([0, 50, 50]), np.array([10, 255, 255])),
                (np.array([170, 50, 50]), np.array([180, 255, 255]))
            ],
            'blue': [
                (np.array([100, 50, 50]), np.array([130, 255, 255]))
            ],
            'green': [
                (np.array([40, 50, 50]), np.array([80, 255, 255]))
            ],
            'yellow': [
                (np.array([20, 50, 50]), np.array([30, 255, 255]))
            ],
            'orange': [
                (np.array([10, 50, 50]), np.array([20, 255, 255]))
            ],
            'purple': [
                (np.array([130, 50, 50]), np.array([160, 255, 255]))
            ],
            'pink': [
                (np.array([160, 50, 50]), np.array([170, 255, 255]))
            ]
        }
        
        target_color_lower = target_color.lower()
        if target_color_lower not in color_ranges:
            return 0.0
        
        # Create mask for target color
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in color_ranges[target_color_lower]:
            mask += cv2.inRange(hsv, lower, upper)
        
        # Calculate percentage of pixels matching color
        total_pixels = mask.size
        matching_pixels = np.count_nonzero(mask)
        color_match_ratio = matching_pixels / total_pixels if total_pixels > 0 else 0.0
        
        return color_match_ratio
    
    def _detect_home_marker(self, frame):
        """
        Detect home marker (red box) using YOLO object detection + color tracking
        
        Args:
            frame: RGB frame from camera
            
        Returns:
            dict with marker info: {'detected': bool, 'center_x': int, 'center_y': int, 'width': int, 'confidence': float, 'color_match': float}
        """
        try:
            # Run YOLO object detection
            results = self.yolo_model(
                frame,
                conf=0.3,  # Confidence threshold
                verbose=False,
                imgsz=config.YOLO_INFERENCE_SIZE,
                max_det=config.YOLO_MAX_DET
            )
            
            if not results or len(results) == 0:
                return {'detected': False, 'center_x': None, 'center_y': None, 'width': None, 'confidence': None, 'color_match': None}
            
            result = results[0]
            
            # Check if we have any detections
            if result.boxes is None or len(result.boxes) == 0:
                return {'detected': False, 'center_x': None, 'center_y': None, 'width': None, 'confidence': None, 'color_match': None}
            
            # Look for the specified object class that also matches the target color
            target_class = self.target_object_class.lower()
            target_color = self.target_color.lower()
            best_detection = None
            best_score = 0.0  # Combined score: confidence * color_match
            
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = self.yolo_model.names[class_id].lower()
                
                # Check if this is the target class
                if target_class in class_name or class_name in target_class:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    
                    # Check color match
                    color_match_ratio = self._check_color_match(frame, (x1, y1, x2, y2), target_color)
                    
                    # Object must match color threshold
                    if color_match_ratio >= self.color_threshold:
                        # Combined score: confidence weighted by color match
                        combined_score = confidence * color_match_ratio
                        
                        if combined_score > best_score:
                            best_score = combined_score
                            width = x2 - x1
                            height = y2 - y1
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            
                            best_detection = {
                                'detected': True,
                                'center_x': center_x,
                                'center_y': center_y,
                                'width': width,
                                'height': height,
                                'confidence': confidence,
                                'color_match': color_match_ratio,
                                'class_name': class_name
                            }
            
            if best_detection:
                return best_detection
            else:
                return {'detected': False, 'center_x': None, 'center_y': None, 'width': None, 'confidence': None, 'color_match': None}
                
        except Exception as e:
            print(f"[TEST] Error in home marker detection: {e}")
            return {'detected': False, 'center_x': None, 'center_y': None, 'width': None, 'confidence': None, 'color_match': None}
    
    def _get_frame(self):
        """Get current camera frame with rotation and color correction"""
        # Capture frame
        array = self.picam2.capture_array(wait=True)  # Returns RGB
        
        # Apply camera rotation if configured
        if config.CAMERA_ROTATION == 180:
            array = cv2.rotate(array, cv2.ROTATE_180)
        elif config.CAMERA_ROTATION == 90:
            array = cv2.rotate(array, cv2.ROTATE_90_CLOCKWISE)
        elif config.CAMERA_ROTATION == 270:
            array = cv2.rotate(array, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Apply flips if configured
        if config.CAMERA_FLIP_HORIZONTAL:
            array = cv2.flip(array, 1)
        if config.CAMERA_FLIP_VERTICAL:
            array = cv2.flip(array, 0)
        
        # Fix color channel swap if needed
        if config.CAMERA_SWAP_RB:
            array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
            array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        
        return array
    
    def run(self):
        """Run the return-to-home test"""
        try:
            # Step 1: Turn hard right for set duration
            print(f"[TEST] Step 1: Turning hard right for {self.turn_duration}s...")
            self.motor.stop()  # Stop before turning
            self.servo.turn_right(1.0)  # Max right turn
            time.sleep(self.turn_duration)
            self.servo.center()  # Center steering
            print("[TEST] Turn complete")
            print()
            
            # Step 2: Scan for red box and drive towards it
            print("[TEST] Step 2: Scanning for red box...")
            print("Press Ctrl+C to stop")
            print()
            
            found_marker = False
            search_start_time = time.time()
            max_search_time = 30.0  # Maximum time to search for marker (30 seconds)
            
            while True:
                # Check if we've been searching too long
                if time.time() - search_start_time > max_search_time:
                    print("[TEST] Timeout: Could not find home marker")
                    break
                
                # Check TOF sensor - stop if too close
                # TOF sensor returns True when triggered (object detected within threshold)
                if self.tof.detect():
                    print(f"[TEST] TOF sensor triggered! Stopping at home marker (target: {self.stop_distance_mm}mm)")
                    self.motor.stop()
                    self.servo.center()
                    found_marker = True
                    break
                
                # Get frame
                frame = self._get_frame()
                
                # Detect home marker
                marker = self._detect_home_marker(frame)
                
                if marker['detected']:
                    if not found_marker:
                        found_marker = True
                        print(f"[TEST] Home marker detected! Class: {marker['class_name']}, "
                              f"Confidence: {marker['confidence']:.2f}, "
                              f"Color match: {marker['color_match']:.1%}")
                    
                    # Calculate steering angle based on marker position
                    center_x = marker['center_x']
                    frame_center_x = config.CAMERA_WIDTH // 2
                    offset = center_x - frame_center_x
                    
                    # Convert offset to steering angle
                    angle = (offset / config.CAMERA_WIDTH) * 90.0  # Convert to angle
                    angle = max(-45.0, min(45.0, angle))  # Clamp to servo range
                    
                    # Set steering towards marker
                    self.servo.set_angle(angle)
                    
                    # Move forward at slow speed
                    self.motor.forward(config.MOTOR_SLOW)
                    
                    # Check TOF sensor again
                    if self.tof.detect():
                        print(f"[TEST] TOF sensor triggered! Stopping at home marker (target: {self.stop_distance_mm}mm)")
                        self.motor.stop()
                        self.servo.center()
                        found_marker = True
                        break
                    
                    # Debug output
                    print(f"[TEST] Driving towards marker: angle={angle:.1f}°, "
                          f"center={center_x}, offset={offset}")
                else:
                    # Marker not found - search by turning slowly
                    if found_marker:
                        # Lost marker - search
                        print("[TEST] Marker lost, searching...")
                        found_marker = False
                    
                    # Turn slowly while searching
                    self.servo.turn_left(0.3)  # Small left turn
                    self.motor.forward(config.MOTOR_SLOW * 0.5)  # Very slow forward
                
                # Small delay to prevent CPU spinning
                time.sleep(0.1)
            
            if found_marker:
                print()
                print("[TEST] ✓ Successfully returned to home!")
            else:
                print()
                print("[TEST] ✗ Failed to return to home")
            
        except KeyboardInterrupt:
            print("\n[TEST] Interrupted by user")
        except Exception as e:
            print(f"\n[TEST] ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            print("[TEST] Cleaning up...")
            self.motor.stop()
            self.servo.center()
            self.picam2.stop()
            if hasattr(self.motor, 'cleanup'):
                self.motor.cleanup()
            if hasattr(self.servo, 'cleanup'):
                self.servo.cleanup()
            print("[TEST] Test complete")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test return-to-home functionality')
    parser.add_argument('--turn-duration', type=float, default=3.0,
                       help='Duration to turn right in seconds (default: 3.0)')
    parser.add_argument('--stop-distance', type=int, default=100,
                       help='Stop distance in mm (default: 100mm = 10cm)')
    parser.add_argument('--object-class', type=str, default='box',
                       help='YOLO object class to detect (default: box)')
    parser.add_argument('--color', type=str, default='red',
                       help='Color of the box (default: red)')
    
    args = parser.parse_args()
    
    # Create and run test
    test = ReturnToHomeTest()
    test.turn_duration = args.turn_duration
    test.stop_distance_mm = args.stop_distance
    test.target_object_class = args.object_class
    test.target_color = args.color
    
    test.run()


if __name__ == '__main__':
    main()

