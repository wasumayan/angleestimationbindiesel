# Pixy2 Raw Video Setup Guide

This guide will help you set up libpixyusb2 to access raw video frames from your Pixy2 camera.

## Step 1: Download and Build libpixyusb2

### Install Dependencies

```bash
sudo apt-get update
sudo apt-get install git libusb-1.0-0-dev g++ build-essential cmake python3-pip
```

### Clone and Build

```bash
# Clone the Pixy2 repository
git clone https://github.com/charmedlabs/pixy2.git
cd pixy2/scripts

# Build libpixyusb2 library
./build_libpixyusb2.sh
```

This will compile the C++ library. The build output will be in `pixy2/build/`.

## Step 2: Install Python Bindings

### Option A: System-wide (requires --break-system-packages)

```bash
cd pixy2/build/python_demos
pip3 install . --break-system-packages
```

### Option B: Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv pixy2_venv

# Activate it
source pixy2_venv/bin/activate

# Install Python bindings
cd pixy2/build/python_demos
pip install .
```

## Step 3: Test Raw Video Access

### Check Available API Functions

First, let's see what functions are available:

```bash
cd ~/angleestimationbindiesel
source ~/pixy2_venv/bin/activate  # if using venv
python3 pixy2_raw_video.py
```

This will:
1. Check what Pixy2 API functions are available
2. Try to access raw video frames
3. Display the video feed if successful

## Step 4: Understanding the API

The Pixy2 library provides several ways to access frames:

### Method 1: Raw Frame API (if available)

Some Pixy2 firmware versions support `pixy_get_frame()` or similar functions. Check the actual API:

```python
from pixy import *
import pixy

# List all available functions
print(dir(pixy))
```

### Method 2: USB Video Mode (Alternative)

If raw frame API is not available, Pixy2 may work as a standard USB video device:

```bash
python3 test_pixy2_video.py
```

This uses OpenCV's `cv2.VideoCapture()` which is simpler and more compatible.

## Step 5: Integration with Your Code

### If Raw Video Works

Update your camera initialization:

```python
from pixy2_raw_video import Pixy2RawVideo

# Instead of Picamera2
self.camera = Pixy2RawVideo(width=640, height=480)

# Get frames (same as before)
frame = self.camera.get_frame()  # Returns RGB numpy array
```

### If USB Video Mode Works

Use OpenCV VideoCapture:

```python
import cv2

# Find which device index works (from test_pixy2_video.py)
self.cap = cv2.VideoCapture(0)  # or 1, 2, etc.

# Get frames
ret, frame_bgr = self.cap.read()
frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
```

## Troubleshooting

### "pixy_get_frame() not found"

This means your Pixy2 firmware doesn't support raw video frame capture. Use USB video mode instead:

```bash
python3 test_pixy2_video.py
```

### "Failed to initialize Pixy2"

1. Check USB connection: `lsusb | grep -i pixy`
2. Check permissions: `sudo chmod 666 /dev/bus/usb/*/*`
3. Try running with sudo: `sudo python3 pixy2_raw_video.py`

### "No module named 'pixy'"

Make sure you installed the Python bindings:
- If using venv: activate it first
- If system-wide: use `--break-system-packages` flag

## Checking the Actual API

The Pixy2 Python bindings may have different function names. Check the actual API:

```python
from pixy import *
import pixy

# See all available functions
for attr in dir(pixy):
    if not attr.startswith('_'):
        print(attr)
```

Common functions you might find:
- `pixy_init()` - Initialize camera
- `pixy_get_frame()` - Get raw frame (if available)
- `pixy_ccc_get_blocks()` - Get color signature blocks
- `pixy_close()` - Close camera

## Next Steps

1. **Test raw video access**: `python3 pixy2_raw_video.py`
2. **If that doesn't work, test USB video mode**: `python3 test_pixy2_video.py`
3. **Choose the method that works** and update your code accordingly

The `pixy2_raw_video.py` script will automatically detect which method works and guide you accordingly.

