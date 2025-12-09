#!/usr/bin/env python3
"""
Combined YOLO + MediaPipe Detection Test
- YOLO for object detection (person, objects)
- MediaPipe Pose for precise pose estimation and arm angle detection
- MediaPipe Hands for gesture recognition
"""

import cv2
import numpy as np
import time
import argparse
import sys
from picamera2 import Picamera2
import warnings
warnings.filterwarnings('ignore')

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not installed!")
    print("Install with: pip3 install --break-system-packages ultralytics")
    sys.exit(1)

try:
    import mediapipe as mp
except ImportError:
    print("ERROR: mediapipe not installed!")
    print("Install with: pip3 install --break-system-packages mediapipe")
    sys.exit(1)

import config


class CombinedDetector:
    """
    Combines YOLO object detection with MediaPipe pose and hand detection
    """
    
    def __init__(self, yolo_model_path='yolo11n.pt', width=640, height=480, yolo_confidence=0.25):
        """
        Initialize combined detector
        
        Args:
            yolo_model_path: Path to YOLO model file
            width: Camera width
            height: Camera height
            yolo_confidence: YOLO confidence threshold
        """
        self.width = width
        self.height = height
        self.yolo_confidence = yolo_confidence
        self.frame_center_x = width // 2
        
        # Initialize YOLO
        print(f"[CombinedDetector] Loading YOLO model: {yolo_model_path}...")
        try:
            self.yolo_model = YOLO(yolo_model_path)
            print("[CombinedDetector] YOLO model loaded")
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
        
        # Find person class ID
        self.person_class_id = None
        for class_id, class_name in self.yolo_model.names.items():
            if class_name == 'person':
                self.person_class_id = class_id
                break
        
        if self.person_class_id is None:
            raise RuntimeError("Person class not found in YOLO model!")
        
        # Initialize MediaPipe Pose
        print("[CombinedDetector] Initializing MediaPipe Pose...")
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # 0=light, 1=full, 2=heavy
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize MediaPipe Hands
        print("[CombinedDetector] Initializing MediaPipe Hands...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize camera
        print("[CombinedDetector] Initializing camera...")
        try:
            self.picam2 = Picamera2()
            preview_config = self.picam2.create_preview_configuration(
                main={"size": (width, height), "format": "RGB888"}
            )
            self.picam2.configure(preview_config)
            self.picam2.start()
            time.sleep(0.5)  # Let camera stabilize
            print(f"[CombinedDetector] Camera started: {width}x{height}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize camera: {e}")
    
    def get_frame(self):
        """
        Get current camera frame
        
        Returns:
            Frame in RGB format (for MediaPipe) and BGR format (for OpenCV display)
        """
        array = self.picam2.capture_array()  # Returns RGB
        frame_rgb = array.copy()
        frame_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)  # Convert to BGR for display
        return frame_rgb, frame_bgr
    
    def calculate_arm_angle(self, landmarks, arm_side='left'):
        """
        Calculate angle of arm raised to the side (60-90 degrees)
        
        Args:
            landmarks: MediaPipe pose landmarks
            arm_side: 'left' or 'right'
            
        Returns:
            Angle in degrees, or None if not detected
        """
        # MediaPipe pose landmark indices
        # Left arm: shoulder=11, elbow=13, wrist=15
        # Right arm: shoulder=12, elbow=14, wrist=16
        
        if arm_side == 'left':
            shoulder_idx = 11
            elbow_idx = 13
            wrist_idx = 15
        else:  # right
            shoulder_idx = 12
            elbow_idx = 14
            wrist_idx = 16
        
        # Get landmark positions
        shoulder = landmarks.landmark[shoulder_idx]
        elbow = landmarks.landmark[elbow_idx]
        wrist = landmarks.landmark[wrist_idx]
        
        # Check visibility
        if (shoulder.visibility < 0.5 or elbow.visibility < 0.5 or wrist.visibility < 0.5):
            return None
        
        # Convert to pixel coordinates
        h, w = self.height, self.width
        shoulder_pt = np.array([shoulder.x * w, shoulder.y * h])
        elbow_pt = np.array([elbow.x * w, elbow.y * h])
        wrist_pt = np.array([wrist.x * w, wrist.y * h])
        
        # Calculate vectors
        upper_arm = elbow_pt - shoulder_pt
        lower_arm = wrist_pt - elbow_pt
        
        # Calculate angle between upper arm and horizontal (pointing to side)
        # We want to detect when arm is raised 60-90 degrees from vertical
        # So we check the angle from horizontal (0-30 degrees from horizontal = 60-90 from vertical)
        
        # Calculate angle of upper arm relative to horizontal
        upper_arm_angle = np.arctan2(upper_arm[1], abs(upper_arm[0])) * 180 / np.pi
        
        # Calculate angle between upper and lower arm (elbow angle)
        elbow_angle = None
        if np.linalg.norm(upper_arm) > 0 and np.linalg.norm(lower_arm) > 0:
            # Normalize vectors
            upper_arm_norm = upper_arm / np.linalg.norm(upper_arm)
            lower_arm_norm = lower_arm / np.linalg.norm(lower_arm)
            
            # Calculate angle between vectors
            dot_product = np.clip(np.dot(upper_arm_norm, lower_arm_norm), -1.0, 1.0)
            elbow_angle = np.arccos(dot_product) * 180 / np.pi
        
        # Check if arm is raised to the side (60-90 degrees from vertical)
        # This means upper arm angle should be between 0-30 degrees from horizontal
        # And wrist should be higher than shoulder (raised up)
        # Also check that arm is extended horizontally (not just up)
        horizontal_extension = abs(upper_arm[0]) > abs(upper_arm[1]) * 0.5  # More horizontal than vertical
        
        # Check if arm is raised (elbow_angle must be valid)
        arm_raised_side = False
        if elbow_angle is not None:
            arm_raised_side = (upper_arm_angle < 30.0 and 
                               wrist_pt[1] < shoulder_pt[1] and  # Wrist above shoulder
                               elbow_angle > 60.0 and elbow_angle < 150.0 and  # Elbow not fully extended
                               horizontal_extension)  # Arm extended horizontally
        
        if arm_raised_side:
            # Return angle from vertical (90 - horizontal angle)
            angle_from_vertical = 90.0 - upper_arm_angle
            return angle_from_vertical
        
        return None
    
    def detect_hand_gesture(self, hand_landmarks):
        """
        Detect hand gesture from MediaPipe hand landmarks
        
        Args:
            hand_landmarks: MediaPipe hand landmarks (normalized coordinates 0-1)
            
        Returns:
            Gesture name: 'stop', 'turn_around', 'turn_left', 'turn_right', 
                         'come', 'go_away', or None
        """
        # MediaPipe hand landmark indices
        # Thumb: 4 (tip), 3 (IP), 2, 1
        # Index: 8 (tip), 7 (PIP), 6, 5
        # Middle: 12 (tip), 11 (PIP), 10, 9
        # Ring: 16 (tip), 15 (PIP), 14, 13
        # Pinky: 20 (tip), 19 (PIP), 18, 17
        # Wrist: 0
        
        landmarks = hand_landmarks.landmark
        
        # Get key points (normalized coordinates 0-1)
        wrist = np.array([landmarks[0].x, landmarks[0].y])
        thumb_tip = np.array([landmarks[4].x, landmarks[4].y])
        index_tip = np.array([landmarks[8].x, landmarks[8].y])
        middle_tip = np.array([landmarks[12].x, landmarks[12].y])
        ring_tip = np.array([landmarks[16].x, landmarks[16].y])
        pinky_tip = np.array([landmarks[20].x, landmarks[20].y])
        
        thumb_ip = np.array([landmarks[3].x, landmarks[3].y])
        index_pip = np.array([landmarks[6].x, landmarks[6].y])
        middle_pip = np.array([landmarks[10].x, landmarks[10].y])
        ring_pip = np.array([landmarks[14].x, landmarks[14].y])
        pinky_pip = np.array([landmarks[18].x, landmarks[18].y])
        
        # Check if fingers are extended (tip is above PIP joint in Y coordinate)
        # Note: In image coordinates, Y increases downward, so "extended" means tip.y < pip.y
        thumb_extended = thumb_tip[1] < thumb_ip[1] - 0.02  # Thumb is special (sideways)
        index_extended = index_tip[1] < index_pip[1] - 0.02
        middle_extended = middle_tip[1] < middle_pip[1] - 0.02
        ring_extended = ring_tip[1] < ring_pip[1] - 0.02
        pinky_extended = pinky_tip[1] < pinky_pip[1] - 0.02
        
        # For thumb, also check if it's extended outward (x coordinate)
        # Left hand: thumb extended means thumb_tip.x < thumb_ip.x
        # Right hand: thumb extended means thumb_tip.x > thumb_ip.x
        # We'll check both cases
        thumb_outward = abs(thumb_tip[0] - thumb_ip[0]) > 0.02
        
        # Calculate finger states
        fingers_up = [thumb_extended and thumb_outward, index_extended, middle_extended, ring_extended, pinky_extended]
        num_fingers = sum(fingers_up)
        
        # Calculate hand direction/orientation
        # Use middle finger and wrist to determine hand orientation
        hand_vector = middle_tip - wrist
        hand_angle = np.arctan2(hand_vector[1], hand_vector[0]) * 180 / np.pi
        
        # Gesture recognition
        
        # STOP: Open palm (all 5 fingers extended)
        if num_fingers == 5:
            return 'stop'
        
        # TURN LEFT: Pointing left (index finger extended, others closed, pointing left)
        if index_extended and not middle_extended and not ring_extended and not pinky_extended:
            # Check if pointing left (angle between -135 and -45 degrees)
            if -135 < hand_angle < -45:
                return 'turn_left'
        
        # TURN RIGHT: Pointing right (index finger extended, others closed, pointing right)
        if index_extended and not middle_extended and not ring_extended and not pinky_extended:
            # Check if pointing right (angle between 45 and 135 degrees)
            if 45 < hand_angle < 135:
                return 'turn_right'
        
        # TURN AROUND: Pointing backward/up (index finger extended, pointing up/backward)
        if index_extended and not middle_extended and not ring_extended and not pinky_extended:
            # Check if pointing backward/up (angle < -135 or > 135 degrees)
            if hand_angle < -135 or hand_angle > 135:
                return 'turn_around'
        
        # COME TOWARDS ME: Beckoning gesture
        # Thumb and index extended, pointing forward/down (beckoning motion)
        if thumb_extended and thumb_outward and index_extended and not middle_extended:
            # Check if pointing forward/down (angle between -45 and 45 degrees)
            if -45 < hand_angle < 45:
                return 'come'
        
        # GO AWAY: Waving away gesture
        # All fingers extended but close together, pointing away/backward
        if num_fingers >= 4:
            # Check if fingers are close together (simplified check)
            finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
            finger_distances = [np.linalg.norm(finger_tips[i] - finger_tips[i+1]) 
                              for i in range(len(finger_tips)-1)]
            avg_distance = np.mean(finger_distances)
            
            # If fingers are close together and pointing away
            if avg_distance < 0.05:  # Threshold for fingers being together
                # Check if pointing away/backward (angle < -135 or > 135 degrees)
                if hand_angle < -135 or hand_angle > 135:
                    return 'go_away'
        
        return None
    
    def detect(self, frame_rgb):
        """
        Run combined detection on frame
        
        Args:
            frame_rgb: RGB frame
            
        Returns:
            dict with detection results
        """
        results = {
            'yolo_objects': [],
            'person_detected': False,
            'person_box': None,
            'pose_landmarks': None,
            'left_arm_raised': False,
            'right_arm_raised': False,
            'left_arm_angle': None,
            'right_arm_angle': None,
            'hand_landmarks': None,
            'hand_gestures': [],
            'angle': None,
            'is_centered': False
        }
        
        # Run YOLO detection
        yolo_results = self.yolo_model(frame_rgb, conf=self.yolo_confidence, verbose=False)
        
        # Process YOLO detections
        person_box = None
        for box in yolo_results[0].boxes:
            class_id = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            confidence = float(box.conf[0])
            
            results['yolo_objects'].append({
                'class_id': class_id,
                'class_name': self.yolo_model.names[class_id],
                'box': (x1, y1, x2, y2),
                'confidence': confidence
            })
            
            # Find person detection
            if class_id == self.person_class_id and person_box is None:
                person_box = (x1, y1, x2, y2)
                results['person_detected'] = True
                results['person_box'] = person_box
                
                # Calculate angle
                person_center_x = (x1 + x2) / 2
                offset = person_center_x - self.frame_center_x
                results['angle'] = (offset / self.width) * 102.0
                results['is_centered'] = abs(offset) < 30
        
        # Run MediaPipe Pose detection
        pose_results = self.pose.process(frame_rgb)
        
        if pose_results.pose_landmarks:
            results['pose_landmarks'] = pose_results.pose_landmarks
            
            # Check arm angles
            left_angle = self.calculate_arm_angle(pose_results.pose_landmarks, 'left')
            right_angle = self.calculate_arm_angle(pose_results.pose_landmarks, 'right')
            
            if left_angle is not None:
                results['left_arm_raised'] = True
                results['left_arm_angle'] = left_angle
            
            if right_angle is not None:
                results['right_arm_raised'] = True
                results['right_arm_angle'] = right_angle
        
        # Run MediaPipe Hands detection
        hand_results = self.hands.process(frame_rgb)
        
        if hand_results.multi_hand_landmarks:
            results['hand_landmarks'] = hand_results.multi_hand_landmarks
            for hand_landmarks in hand_results.multi_hand_landmarks:
                gesture = self.detect_hand_gesture(hand_landmarks)
                if gesture:
                    results['hand_gestures'].append(gesture)
        else:
            results['hand_landmarks'] = None
        
        return results
    
    def stop(self):
        """Stop camera and cleanup"""
        if self.picam2:
            self.picam2.stop()
            self.picam2.close()
        self.pose.close()
        self.hands.close()
        print("[CombinedDetector] Stopped")


def detect_pose_type(results):
    """
    Detect what pose is being performed based on MediaPipe landmarks
    
    Args:
        results: Detection results dict
        
    Returns:
        String describing the pose
    """
    if not results['pose_landmarks']:
        return None
    
    # Check for arm raised
    if results['left_arm_raised'] or results['right_arm_raised']:
        if results['left_arm_raised'] and results['right_arm_raised']:
            return "Both Arms Raised"
        elif results['left_arm_raised']:
            return "Left Arm Raised"
        else:
            return "Right Arm Raised"
    
    # Check for hand gestures
    if results['hand_gestures']:
        gesture_names = {
            'stop': 'Stop Signal',
            'turn_left': 'Pointing Left',
            'turn_right': 'Pointing Right',
            'turn_around': 'Pointing Back',
            'come': 'Come Here',
            'go_away': 'Go Away'
        }
        gestures = [gesture_names.get(g, g.upper()) for g in results['hand_gestures']]
        return ", ".join(gestures)
    
    # Default: standing/neutral pose
    return "Standing"


def draw_detections(frame_bgr, results, detector):
    """
    Draw detection results on frame with combined YOLO + MediaPipe overlays
    
    Args:
        frame_bgr: BGR frame for drawing
        results: Detection results dict
        detector: CombinedDetector instance
    """
    # Draw YOLO object detections with thinner boxes and smaller font
    for obj in results['yolo_objects']:
        x1, y1, x2, y2 = obj['box']
        class_name = obj['class_name']
        confidence = obj['confidence']
        
        # Color: green for person, blue for others
        color = (0, 255, 0) if class_name == 'person' else (255, 0, 0)
        
        # Thinner bounding box (thickness=1 instead of 2)
        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 1)
        
        # Smaller font (0.35 instead of 0.5, thickness=1 instead of 2)
        label = f"{class_name} {confidence:.2f}"
        cv2.putText(frame_bgr, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)
    
    # Draw MediaPipe pose landmarks (skeleton overlay)
    if results['pose_landmarks']:
        detector.mp_drawing.draw_landmarks(
            frame_bgr,
            results['pose_landmarks'],
            detector.mp_pose.POSE_CONNECTIONS,
            detector.mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1, circle_radius=1),
            detector.mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=1)
        )
    
    # Draw MediaPipe hand landmarks (overlay on hands)
    if results.get('hand_landmarks'):
        for hand_landmarks in results['hand_landmarks']:
            detector.mp_drawing.draw_landmarks(
                frame_bgr,
                hand_landmarks,
                detector.mp_hands.HAND_CONNECTIONS,
                detector.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                detector.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=1)
            )
    
    # Draw pose type at top center
    pose_type = detect_pose_type(results)
    if pose_type:
        # Get text size for centering
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(pose_type, font, font_scale, thickness)
        
        # Center the text
        x_pos = (frame_bgr.shape[1] - text_width) // 2
        y_pos = 25
        
        # Draw background rectangle for better visibility
        cv2.rectangle(frame_bgr, 
                     (x_pos - 5, y_pos - text_height - 5),
                     (x_pos + text_width + 5, y_pos + baseline + 5),
                     (0, 0, 0), -1)
        
        # Draw pose text
        cv2.putText(frame_bgr, pose_type, (x_pos, y_pos),
                   font, font_scale, (255, 255, 0), thickness)
    
    # Draw status info in top-left corner (smaller font)
    y_offset = 30
    font_scale = 0.4
    thickness = 1
    
    if results['left_arm_raised']:
        text = f"L Arm: {results['left_arm_angle']:.0f}°"
        cv2.putText(frame_bgr, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
        y_offset += 20
    
    if results['right_arm_raised']:
        text = f"R Arm: {results['right_arm_angle']:.0f}°"
        cv2.putText(frame_bgr, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)
        y_offset += 20
    
    # Draw hand gestures (smaller)
    if results['hand_gestures']:
        for gesture in results['hand_gestures']:
            gesture_text = f"Gesture: {gesture.upper()}"
            cv2.putText(frame_bgr, gesture_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 255), thickness)
            y_offset += 20
    
    # Draw person angle info at bottom (smaller)
    if results['person_detected']:
        if results['angle'] is not None:
            angle_text = f"Angle: {results['angle']:.1f}°"
            cv2.putText(frame_bgr, angle_text, (10, frame_bgr.shape[0] - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness)
        
        if results['is_centered']:
            cv2.putText(frame_bgr, "CENTERED", (10, frame_bgr.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)


def main():
    parser = argparse.ArgumentParser(description='Test combined YOLO + MediaPipe detection')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--fps', action='store_true', help='Show FPS counter')
    parser.add_argument('--yolo-conf', type=float, default=0.25, help='YOLO confidence threshold')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Combined YOLO + MediaPipe Detection Test")
    print("=" * 70)
    print("Features:")
    print("  - YOLO: Object detection (person, objects)")
    print("  - MediaPipe Pose: Precise pose estimation")
    print("  - Arm angle detection: 60-90 degrees raised to side")
    print("  - Hand gestures: stop, turn_left, turn_right, turn_around, come, go_away")
    print()
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 'd' to toggle debug mode")
    print("=" * 70)
    print()
    
    debug_mode = args.debug
    
    try:
        # Initialize detector
        detector = CombinedDetector(
            yolo_model_path=config.YOLO_MODEL,
            width=config.CAMERA_WIDTH,
            height=config.CAMERA_HEIGHT,
            yolo_confidence=args.yolo_conf
        )
        
        print("[TEST] Combined detector initialized")
        print("[TEST] Starting camera feed...")
        print()
        
        # FPS tracking
        fps_counter = 0
        fps_start_time = time.time()
        fps = 0
        
        # Start OpenCV window
        cv2.startWindowThread()
        
        while True:
            # Get frames
            frame_rgb, frame_bgr = detector.get_frame()
            
            # Run detection
            results = detector.detect(frame_rgb)
            
            # Draw detections
            draw_detections(frame_bgr, results, detector)
            
            # Draw FPS
            if args.fps:
                fps_counter += 1
                if fps_counter % 10 == 0:
                    fps_end_time = time.time()
                    fps = 10 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                fps_text = f'FPS: {fps:.1f}'
                cv2.putText(frame_bgr, fps_text, (frame_bgr.shape[1] - 150, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Debug mode output
            if debug_mode:
                debug_y = frame_bgr.shape[0] - 150
                cv2.putText(frame_bgr, "DEBUG MODE", (10, debug_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                debug_y += 20
                
                if results['person_detected']:
                    cv2.putText(frame_bgr, f"Person box: {results['person_box']}", (10, debug_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    debug_y += 15
                
                if results['pose_landmarks']:
                    cv2.putText(frame_bgr, "Pose detected", (10, debug_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                    debug_y += 15
                
                if results['hand_gestures']:
                    cv2.putText(frame_bgr, f"Gestures: {results['hand_gestures']}", (10, debug_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
            
            # Display frame
            cv2.imshow('Combined Detection Test - Press q to quit', frame_bgr)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('d'):
                debug_mode = not debug_mode
                print(f"[TEST] Debug mode: {'ON' if debug_mode else 'OFF'}")
            
            # Print to terminal periodically
            if results['person_detected']:
                output = f"[TEST] Person detected: angle={results['angle']:.1f}°"
                if results['left_arm_raised']:
                    output += f", LEFT ARM: {results['left_arm_angle']:.1f}°"
                if results['right_arm_raised']:
                    output += f", RIGHT ARM: {results['right_arm_angle']:.1f}°"
                if results['hand_gestures']:
                    output += f", GESTURES: {results['hand_gestures']}"
                print(output)
    
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    except Exception as e:
        print(f"\n[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'detector' in locals():
            detector.stop()
        cv2.destroyAllWindows()
        print("[TEST] Test complete")


if __name__ == '__main__':
    main()

