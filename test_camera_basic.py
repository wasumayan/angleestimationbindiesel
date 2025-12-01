#!/usr/bin/env python3
"""
Basic camera functionality test
Tests camera capture, display, and basic operations
"""

# Fix OpenCV import if needed
try:
    import cv2
except ImportError:
    import sys
    import os
    system_paths = [
        '/usr/lib/python3/dist-packages',
        '/usr/local/lib/python3/dist-packages',
    ]
    for path in system_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
    try:
        import cv2
    except ImportError:
        print("ERROR: OpenCV not found!")
        print("Install with: sudo apt-get install python3-opencv")
        sys.exit(1)

import numpy as np
import time


def test_camera_detection():
    """Test if camera is detected"""
    print("=" * 70)
    print("Camera Detection Test")
    print("=" * 70)
    
    # Try different camera indices
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get camera info
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"\n✓ Camera found at index {i}")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps}")
            
            cap.release()
            return i
    
    print("\n✗ No camera detected")
    return None


def test_camera_capture(camera_index=0, duration=5):
    """Test capturing frames from camera"""
    print("\n" + "=" * 70)
    print("Camera Capture Test")
    print("=" * 70)
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"✗ Could not open camera {camera_index}")
        return False
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"\nCapturing for {duration} seconds...")
    print("Press 'q' to quit early\n")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            
            if not ret:
                print("✗ Failed to read frame")
                break
            
            frame_count += 1
            
            # Display frame
            cv2.imshow('Camera Test', frame)
            
            # Show FPS
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n✓ Capture test complete")
        print(f"  Frames captured: {frame_count}")
        print(f"  Average FPS: {avg_fps:.1f}")
        print(f"  Duration: {elapsed:.2f} seconds")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        return False
    finally:
        cap.release()
        cv2.destroyAllWindows()


def test_camera_properties(camera_index=0):
    """Test camera properties and capabilities"""
    print("\n" + "=" * 70)
    print("Camera Properties Test")
    print("=" * 70)
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"✗ Could not open camera {camera_index}")
        return
    
    properties = {
        'Width': cv2.CAP_PROP_FRAME_WIDTH,
        'Height': cv2.CAP_PROP_FRAME_HEIGHT,
        'FPS': cv2.CAP_PROP_FPS,
        'Brightness': cv2.CAP_PROP_BRIGHTNESS,
        'Contrast': cv2.CAP_PROP_CONTRAST,
        'Saturation': cv2.CAP_PROP_SATURATION,
    }
    
    print("\nCamera Properties:")
    for name, prop in properties.items():
        value = cap.get(prop)
        print(f"  {name}: {value}")
    
    cap.release()


def main():
    """Main test function"""
    print("=" * 70)
    print("Basic Camera Functionality Test")
    print("=" * 70)
    
    # Test 1: Detect camera
    camera_index = test_camera_detection()
    
    if camera_index is None:
        print("\n✗ Camera not detected. Check:")
        print("  1. Camera is connected")
        print("  2. Camera is enabled: sudo raspi-config")
        print("  3. Permissions: sudo usermod -a -G video $USER")
        return
    
    # Test 2: Camera properties
    test_camera_properties(camera_index)
    
    # Test 3: Capture test
    input("\nPress Enter to start capture test...")
    test_camera_capture(camera_index, duration=10)
    
    print("\n" + "=" * 70)
    print("Camera Test Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()

