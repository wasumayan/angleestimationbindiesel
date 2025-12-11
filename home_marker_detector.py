#!/usr/bin/env python3
"""
Home Marker Detection Module
Detects a red box using YOLO object detection + OpenCV color tracking
Hardcoded for red box detection
"""

import cv2
import numpy as np
from logger import setup_logger, log_error

logger = setup_logger(__name__)


def check_color_match_red(frame, bbox):
    """
    Check if object in bounding box matches red color using OpenCV
    
    Args:
        frame: RGB frame
        bbox: Bounding box (x1, y1, x2, y2)
        
    Returns:
        float: Percentage of pixels matching red color (0.0-1.0)
    """
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
    
    # Red color ranges in HSV (red wraps around 0/180)
    # Lower red range (0-10)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    # Upper red range (170-180)
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Create mask for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2
    
    # Calculate percentage of pixels matching red color
    total_pixels = mask.size
    matching_pixels = np.count_nonzero(mask)
    color_match_ratio = matching_pixels / total_pixels if total_pixels > 0 else 0.0
    
    return color_match_ratio


def detect_red_box(yolo_model, frame, confidence_threshold=0.3, color_threshold=0.3):
    """
    Detect red box using YOLO object detection + OpenCV color tracking
    Hardcoded for red box detection
    
    Args:
        yolo_model: YOLO model instance
        frame: RGB frame from camera
        confidence_threshold: Minimum YOLO confidence (default: 0.3)
        color_threshold: Minimum color match ratio (default: 0.3 = 30%)
        
    Returns:
        dict with marker info: {
            'detected': bool,
            'center_x': int,
            'center_y': int,
            'width': int,
            'height': int,
            'area': int,
            'confidence': float,
            'color_match': float,
            'class_name': str
        }
    """
    if yolo_model is None:
        return {
            'detected': False,
            'center_x': None,
            'center_y': None,
            'width': None,
            'height': None,
            'area': None,
            'confidence': None,
            'color_match': None,
            'class_name': None
        }
    
    try:
        # Run YOLO object detection
        results = yolo_model(
            frame,
            conf=confidence_threshold,
            verbose=False
        )
        
        if not results or len(results) == 0:
            return {
                'detected': False,
                'center_x': None,
                'center_y': None,
                'width': None,
                'height': None,
                'area': None,
                'confidence': None,
                'color_match': None,
                'class_name': None
            }
        
        result = results[0]
        
        # Check if we have any detections
        if result.boxes is None or len(result.boxes) == 0:
            return {
                'detected': False,
                'center_x': None,
                'center_y': None,
                'width': None,
                'height': None,
                'area': None,
                'confidence': None,
                'color_match': None,
                'class_name': None
            }
        
        # Look for box objects that match red color
        target_class = 'box'  # Hardcoded for box
        best_detection = None
        best_score = 0.0  # Combined score: confidence * color_match
        
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = yolo_model.names[class_id].lower()
            
            # Check if this is a box (or similar object)
            if target_class in class_name or class_name in target_class:
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                
                # Check color match using OpenCV (hardcoded for red)
                color_match_ratio = check_color_match_red(frame, (x1, y1, x2, y2))
                
                # Object must match red color threshold
                if color_match_ratio >= color_threshold:
                    # Combined score: confidence weighted by color match
                    combined_score = confidence * color_match_ratio
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        width = x2 - x1
                        height = y2 - y1
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        area = width * height
                        
                        best_detection = {
                            'detected': True,
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': width,
                            'height': height,
                            'area': area,
                            'confidence': confidence,
                            'color_match': color_match_ratio,
                            'class_name': class_name
                        }
        
        if best_detection:
            return best_detection
        else:
            return {
                'detected': False,
                'center_x': None,
                'center_y': None,
                'width': None,
                'height': None,
                'area': None,
                'confidence': None,
                'color_match': None,
                'class_name': None
            }
                
    except Exception as e:
        log_error(logger, e, "Error in red box detection")
        return {
            'detected': False,
            'center_x': None,
            'center_y': None,
            'width': None,
            'height': None,
            'area': None,
            'confidence': None,
            'color_match': None,
            'class_name': None
        }


def draw_overlay(frame, marker, yolo_result=None):
    """
    Draw detection overlay on frame showing red box detection
    
    Args:
        frame: RGB frame
        marker: Detection result dict from detect_red_box()
        yolo_result: Optional YOLO result object for default overlay
        
    Returns:
        Annotated frame in BGR format
    """
    # Convert RGB to BGR for OpenCV display
    annotated_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    
    # Use YOLO's built-in plot() if available for default overlays
    if yolo_result is not None:
        try:
            annotated_frame = yolo_result.plot()  # YOLO's default overlay (returns BGR)
        except Exception as e:
            logger.warning(f"YOLO plot() failed: {e}, using frame as-is")
            annotated_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Draw red box detection overlay
    if marker['detected']:
        # Draw bounding box
        x1 = marker['center_x'] - marker['width'] // 2
        y1 = marker['center_y'] - marker['height'] // 2
        x2 = marker['center_x'] + marker['width'] // 2
        y2 = marker['center_y'] + marker['height'] // 2
        
        # Green box for detected red box
        color = (0, 255, 0)  # Green in BGR
        thickness = 3
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
        
        # Draw center point
        cv2.circle(annotated_frame, (marker['center_x'], marker['center_y']), 5, color, -1)
        
        # Draw label with detection info
        label = f"RED BOX: {marker['class_name']}"
        conf_text = f"Conf: {marker['confidence']:.2f}"
        color_text = f"Color Match: {marker['color_match']:.1%}"
        
        # Background for text (for better visibility)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness_text = 2
        
        # Calculate text size
        (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, thickness_text)
        (conf_w, conf_h), _ = cv2.getTextSize(conf_text, font, font_scale, thickness_text)
        (color_w, color_h), _ = cv2.getTextSize(color_text, font, font_scale, thickness_text)
        
        # Draw text background
        text_x = x1
        text_y = y1 - 10
        if text_y < 30:
            text_y = y2 + 30
        
        cv2.rectangle(annotated_frame, 
                     (text_x - 5, text_y - label_h - 5),
                     (text_x + max(label_w, conf_w, color_w) + 5, text_y + conf_h + color_h + 10),
                     (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(annotated_frame, label, (text_x, text_y),
                   font, font_scale, color, thickness_text)
        cv2.putText(annotated_frame, conf_text, (text_x, text_y + conf_h + 5),
                   font, font_scale, color, thickness_text)
        cv2.putText(annotated_frame, color_text, (text_x, text_y + conf_h + color_h + 10),
                   font, font_scale, color, thickness_text)
        
        # Draw status at top
        status_text = "RED BOX DETECTED!"
        cv2.putText(annotated_frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    else:
        # No detection
        status_text = "No red box detected"
        cv2.putText(annotated_frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # Red text
    
    return annotated_frame


def main():
    """Test home marker detector with camera feed and visualization"""
    import sys
    import time
    import argparse
    from pathlib import Path
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        import config
        from picamera2 import Picamera2
        from ultralytics import YOLO
    except ImportError as e:
        print(f"ERROR: Missing required module: {e}")
        print("Install with: pip install ultralytics picamera2")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Test red box detection')
    parser.add_argument('--confidence', type=float, default=0.3,
                       help='YOLO confidence threshold (default: 0.3)')
    parser.add_argument('--color-threshold', type=float, default=0.3,
                       help='Color match threshold (default: 0.3 = 30%%)')
    parser.add_argument('--fps', action='store_true',
                       help='Show FPS counter')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Red Box Detection Test")
    print("=" * 70)
    print(f"Confidence threshold: {args.confidence}")
    print(f"Color match threshold: {args.color_threshold:.1%}")
    print("Press 'q' to quit")
    print("=" * 70)
    print()
    
    # Initialize YOLO model - use regular YOLO model (not OBB)
    print("[TEST] Initializing YOLO model...")
    try:
        yolo_model = YOLO(config.YOLO_MODEL)
        print(f"[TEST] YOLO model loaded: {config.YOLO_MODEL}")
    except Exception as e1:
        # Fallback: if NCNN failed, try PyTorch
        if config.USE_NCNN and config.YOLO_MODEL.endswith('_ncnn_model'):
            fallback_path = config.YOLO_MODEL.replace('_ncnn_model', '.pt')
            print(f"[TEST] NCNN model not found, trying PyTorch: {fallback_path}")
            yolo_model = YOLO(fallback_path)
            print(f"[TEST] PyTorch model loaded: {fallback_path}")
        else:
            raise RuntimeError(f"Failed to load YOLO model: {e1}") from e1
    
    # Initialize camera
    print("[TEST] Initializing camera...")
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(
        main={"size": (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), "format": "RGB888"},
        controls={"FrameRate": config.CAMERA_FPS}
    )
    picam2.configure(preview_config)
    picam2.start()
    time.sleep(1.5)  # Wait for camera to initialize
    print(f"[TEST] Camera started: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
    print()
    
    # FPS tracking
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Get frame
            frame = picam2.capture_array(wait=True)  # Returns RGB
            
            # Apply camera rotation if configured
            if config.CAMERA_ROTATION == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif config.CAMERA_ROTATION == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif config.CAMERA_ROTATION == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Apply flips if configured
            if config.CAMERA_FLIP_HORIZONTAL:
                frame = cv2.flip(frame, 1)
            if config.CAMERA_FLIP_VERTICAL:
                frame = cv2.flip(frame, 0)
            
            # Fix color channel swap if needed
            if config.CAMERA_SWAP_RB:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Run YOLO detection to get result object for overlay
            yolo_results = yolo_model(
                frame,
                conf=args.confidence,
                verbose=False
            )
            yolo_result = yolo_results[0] if yolo_results else None
            
            # Detect red box
            marker = detect_red_box(
                yolo_model,
                frame,
                confidence_threshold=args.confidence,
                color_threshold=args.color_threshold
            )
            
            # Draw overlay
            annotated_frame = draw_overlay(frame, marker, yolo_result)
            
            # Calculate FPS
            frame_count += 1
            if args.fps:
                elapsed = time.time() - start_time
                if elapsed > 0:
                    fps = frame_count / elapsed
                    fps_text = f'FPS: {fps:.1f}'
                    cv2.putText(annotated_frame, fps_text, 
                               (annotated_frame.shape[1] - 150, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Red Box Detection Test', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Small delay to prevent CPU spinning
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n[TEST] Interrupted by user")
    except Exception as e:
        print(f"\n[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("[TEST] Cleaning up...")
        picam2.stop()
        cv2.destroyAllWindows()
        print("[TEST] Test complete")


if __name__ == '__main__':
    main()

