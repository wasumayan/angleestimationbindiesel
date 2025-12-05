# Gesture Detection Setup Guide

## MediaPipe Installation Issues

MediaPipe can be difficult to install on Raspberry Pi, especially in virtual environments. Here are several solutions:

## Solution 1: Install System-Wide (Recommended for Pi)

Exit your virtual environment and install system-wide:

```bash
# Exit virtual environment
deactivate

# Install MediaPipe system-wide
pip3 install --break-system-packages mediapipe

# Then run the script (outside venv)
python3 combined_detection.py
```

## Solution 2: Use System Site Packages in Venv

Recreate your virtual environment with system site packages:

```bash
# Exit current venv
deactivate

# Remove old venv
rm -rf venv

# Create new venv with system site packages
python3 -m venv --system-site-packages venv

# Activate it
source venv/bin/activate

# Now MediaPipe should be accessible
python3 combined_detection.py
```

## Solution 3: Install from Source (If pip fails)

If pip installation fails, try building from source or using alternative methods:

```bash
# Try installing specific version
pip3 install --break-system-packages mediapipe==0.10.7

# Or try with different index
pip3 install --break-system-packages --index-url https://pypi.org/simple mediapipe
```

## Solution 4: Use Alternative Gesture Detection

If MediaPipe continues to fail, you can use a simpler angle-based detection without MediaPipe. The script will work without gesture detection - it will just skip that feature.

## Solution 5: Check Architecture Compatibility

MediaPipe may not have wheels for your specific architecture. Check:

```bash
# Check your Python version
python3 --version

# Check architecture
uname -m

# MediaPipe requires Python 3.8-3.11 and ARM64 or x86_64
# For ARM32 (armv7l), you may need to build from source
```

## Troubleshooting

### "No matching distribution found"
- MediaPipe may not have pre-built wheels for your Python version/architecture
- Try installing system-wide instead of in venv
- Check if you're using Python 3.8-3.11 (MediaPipe requirement)

### "Could not find a version"
- Your architecture (e.g., ARM32) may not be supported
- Try Solution 2 (system site packages) or Solution 4 (disable gesture detection)

### Performance Issues
- MediaPipe can be slow on older Raspberry Pi models
- Use `--no-gesture` flag to disable if performance is poor
- Lower camera resolution: `--width 640 --height 480`

## Running Without Gesture Detection

The script will work fine without MediaPipe - it just won't detect gestures:

```bash
# Run with gesture detection disabled
python3 combined_detection.py --no-gesture

# Or just run normally - it will warn but continue
python3 combined_detection.py
```

You'll still get:
- ✅ YOLO object detection
- ✅ Color detection
- ❌ Gesture detection (disabled)

## Alternative: Simple Gesture Detection

If MediaPipe is too complex, we could implement a simpler gesture detection using:
- YOLO person detection bounding box aspect ratio
- Color detection on clothing/arm bands
- Motion detection in specific regions

Let me know if you'd like me to implement a simpler alternative!

