#!/usr/bin/env python3
"""
Simple implementation for Bin Diesel project:
1. Waits for wake word "bin diesel"
2. Once wake word detected, camera looks for colored flag
3. Calculates angle relative to car
4. Sends angle to PSoC
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

import speech_recognition as sr
import numpy as np
import time
from psoc_communicator import PSoCCommunicator


class ColorFlagDetector:
    """Detects colored flag in camera frame"""
    
    def __init__(self, color='red', camera_index=0, horizontal_fov=102.0):
        """
        Initialize color flag detector
        
        Args:
            color: Color to detect ('red', 'green', 'blue', 'yellow')
            camera_index: Camera device index
            horizontal_fov: Horizontal field of view in degrees (default 102 for Camera Module 3 Wide)
        """
        self.color = color.lower()
        self.camera_index = camera_index
        self.horizontal_fov = horizontal_fov
        self.cap = None
        
        # Define HSV color ranges for different colors
        self.color_ranges = {
            'red': [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Lower red
                (np.array([170, 100, 100]), np.array([180, 255, 255]))  # Upper red
            ],
            'green': [
                (np.array([40, 50, 50]), np.array([80, 255, 255]))
            ],
            'blue': [
                (np.array([100, 50, 50]), np.array([130, 255, 255]))
            ],
            'yellow': [
                (np.array([20, 100, 100]), np.array([30, 255, 255]))
            ]
        }
    
    def start_camera(self, width=640, height=480):
        """Initialize camera"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        print(f"Camera started: {width}x{height}")
        return True
    
    def detect_flag(self):
        """
        Detect colored flag in current frame
        
        Returns:
            (center_x, center_y) of flag or None if not detected
        """
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get color range for selected color
        if self.color not in self.color_ranges:
            print(f"Warning: Unknown color '{self.color}', using red")
            color_ranges = self.color_ranges['red']
        else:
            color_ranges = self.color_ranges[self.color]
        
        # Create mask for color
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in color_ranges:
            mask += cv2.inRange(hsv, lower, upper)
        
        # Apply morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None
        
        # Find largest contour (assumed to be the flag)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Filter by minimum area to reduce noise
        if cv2.contourArea(largest_contour) < 500:
            return None
        
        # Calculate center of flag
        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            return None
        
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        
        return (center_x, center_y)
    
    def calculate_angle(self, flag_center, frame_width):
        """
        Calculate angle of flag relative to car center
        
        Args:
            flag_center: (x, y) tuple of flag center
            frame_width: Width of camera frame
            
        Returns:
            Angle in degrees (-90 to +90, negative = left, positive = right)
        """
        if flag_center is None:
            return None
        
        center_x, center_y = flag_center
        frame_center_x = frame_width / 2
        
        # Calculate horizontal offset
        offset = center_x - frame_center_x
        
        # Convert pixel offset to angle using camera's horizontal FOV
        # Camera Module 3 Wide has 102° horizontal FOV
        angle = (offset / frame_width) * self.horizontal_fov
        
        return angle
    
    def cleanup(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()


class WakeWordListener:
    """Listens for wake word"""
    
    def __init__(self, wake_word="bin diesel"):
        """
        Initialize wake word listener
        
        Args:
            wake_word: Wake word phrase to listen for
        """
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    
    def listen_for_wake_word(self):
        """
        Listen for wake word
        
        Returns:
            True when wake word is detected
        """
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print(f"Listening for wake word: '{self.wake_word}'...")
            
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if self.wake_word in text:
                        print(f"Wake word '{self.wake_word}' detected!")
                        return True
                except sr.UnknownValueError:
                    continue
                except sr.WaitTimeoutError:
                    continue
                except sr.RequestError as e:
                    print(f"Error with speech recognition: {e}")
                    continue


def main():
    """Main function"""
    print("=" * 70)
    print("Bin Diesel Simple Implementation")
    print("=" * 70)
    
    # Initialize components
    wake_word_listener = WakeWordListener(wake_word="bin diesel")
    flag_detector = ColorFlagDetector(color='red', camera_index=0)
    psoc = PSoCCommunicator(port='/dev/ttyUSB0', baudrate=115200)
    
    # Connect to PSoC
    if not psoc.connect():
        print("Warning: Could not connect to PSoC. Continuing anyway...")
    
    try:
        while True:
            # Step 1: Wait for wake word
            print("\nWaiting for wake word...")
            wake_word_listener.listen_for_wake_word()
            
            # Step 2: Start camera and look for flag
            print("Wake word detected! Starting camera...")
            if not flag_detector.start_camera():
                print("Error: Could not start camera")
                continue
            
            print("Looking for colored flag...")
            flag_found = False
            timeout = 10.0  # Look for flag for 10 seconds
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                flag_center = flag_detector.detect_flag()
                
                if flag_center is not None:
                    flag_found = True
                    print(f"Flag detected at position: {flag_center}")
                    
                    # Step 3: Calculate angle
                    # Get frame width (assuming 640 from start_camera)
                    frame_width = 640
                    angle = flag_detector.calculate_angle(flag_center, frame_width)
                    
                    if angle is not None:
                        print(f"Calculated angle: {angle:.2f} degrees")
                        
                        # Step 4: Send angle to PSoC
                        if psoc.send_angle_simple(angle):
                            print(f"Angle sent to PSoC: {angle:.2f} degrees")
                        else:
                            print("Error sending angle to PSoC")
                    
                    # Wait a bit before next detection
                    time.sleep(0.1)
                else:
                    # Show that we're still looking
                    if int(time.time() - start_time) % 2 == 0:
                        print(".", end="", flush=True)
                    time.sleep(0.1)
            
            if not flag_found:
                print("\nFlag not found within timeout period")
            
            # Cleanup camera
            flag_detector.cleanup()
            print("\nReturning to wake word listening...")
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        flag_detector.cleanup()
        psoc.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()

