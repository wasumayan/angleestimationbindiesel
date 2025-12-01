# Obstacle Avoidance Research and Libraries

## Overview

For autonomous obstacle avoidance on Raspberry Pi, we need to detect obstacles in the camera view and plan safe paths around them.

## Methods and Libraries

### 1. Monocular Depth Estimation

**Libraries:**
- **MiDaS** (Mixed Dataset for Monocular Depth Estimation)
  - GitHub: https://github.com/isl-org/MiDaS
  - Pre-trained models for depth estimation from single camera
  - Works on Raspberry Pi (may need optimization)

- **DPT (Dense Prediction Transformer)**
  - Part of MiDaS project
  - More accurate but slower

**Installation:**
```bash
pip3 install torch torchvision
pip3 install transformers
# Download MiDaS model
```

**Pros:**
- No additional hardware needed
- Works with single camera
- Good for indoor/outdoor

**Cons:**
- Computationally intensive
- May be slow on Pi 4
- Less accurate than stereo/depth sensors

### 2. Edge Detection + Size Estimation

**Method:**
- Use OpenCV edge detection (Canny)
- Estimate obstacle size based on position in frame
- Bottom of frame = closer, larger = closer

**Implementation:**
- Already implemented in `obstacle_detector.py`
- Simple and fast
- Good for basic obstacle avoidance

**Pros:**
- Very fast
- No additional libraries
- Works in real-time

**Cons:**
- Less accurate
- May have false positives
- Doesn't give actual distance

### 3. Stereo Vision

**Libraries:**
- **OpenCV Stereo Vision**
  - Requires two cameras
  - More accurate depth estimation
  - Real-time capable

**Pros:**
- Accurate depth maps
- Real-time performance possible
- No additional hardware (if you have 2 cameras)

**Cons:**
- Requires two cameras
- Calibration needed
- More complex setup

### 4. Ultrasonic Sensors (Hardware)

**Libraries:**
- **RPi.GPIO** or **gpiozero**
  - Direct hardware interface
  - Very reliable
  - Real-time response

**Pros:**
- Very accurate distance
- Fast response
- Reliable

**Cons:**
- Requires additional hardware
- Limited field of view
- Need multiple sensors for full coverage

### 5. LiDAR (Hardware)

**Libraries:**
- Various depending on LiDAR model
- Most accurate
- 360-degree coverage

**Pros:**
- Most accurate
- Full 360-degree view
- Industry standard

**Cons:**
- Expensive
- Additional hardware
- May be overkill for this project

## Recommended Approach for Your Project

### Phase 1: Simple Edge Detection (Current)
- Already implemented
- Fast and works now
- Good for initial testing

### Phase 2: Enhanced Edge Detection
- Improve with:
  - Contour analysis
  - Motion detection
  - Better size estimation
  - Grid-based obstacle map

### Phase 3: Monocular Depth (If Needed)
- Use MiDaS for better accuracy
- May need to optimize for Pi 4
- Consider using smaller model

### Phase 4: Hardware Sensors (If Needed)
- Add ultrasonic sensors
- More reliable for critical obstacles
- Combine with vision

## Implementation Priority

1. **Start with current edge detection** - it works and is fast
2. **Enhance with better algorithms** - improve accuracy
3. **Add hardware sensors** - if vision isn't sufficient
4. **Consider depth estimation** - if more accuracy needed

## Libraries to Install (for enhanced methods)

```bash
# For enhanced edge detection (already have)
# OpenCV already installed

# For monocular depth (optional, Phase 3)
pip3 install torch torchvision
pip3 install transformers

# For hardware sensors (if adding)
pip3 install RPi.GPIO
# or
pip3 install gpiozero
```

## Code Examples

### Enhanced Edge Detection (Recommended Next Step)

```python
import cv2
import numpy as np

def detect_obstacles_enhanced(frame):
    """Enhanced obstacle detection with better filtering"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Use bottom portion (where obstacles would be)
    h, w = frame.shape[:2]
    roi = gray[int(h*0.4):, :]  # Bottom 60%
    
    # Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(roi, (5, 5), 0)
    
    # Adaptive threshold for better edge detection
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    obstacles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Filter small noise
            x, y, w_box, h_box = cv2.boundingRect(contour)
            # Estimate distance based on size and position
            size = max(w_box, h_box)
            y_pos = y + int(h*0.4)  # Adjust for ROI offset
            
            # Larger and lower = closer
            estimated_distance = 2.0 / (size / 100.0 + 0.1)
            
            obstacles.append({
                'x': x + w_box // 2,
                'y': y_pos,
                'size': size,
                'distance': estimated_distance
            })
    
    return obstacles
```

## Next Steps

1. Test current edge detection method
2. Enhance with better algorithms
3. Test in real environment
4. Add hardware sensors if needed

