# Object Detection Setup Guide

## Installation on Raspberry Pi

### 1. Pull Latest Changes
```bash
cd ~/angleestimationbindiesel  # or wherever your project is
git pull origin main
```

### 2. Install TensorFlow Lite Support

**Important:** `tflite-support` requires Python 3.7-3.9. If you're using Python 3.10+, you may need to:
- Use a virtual environment with Python 3.9, OR
- Downgrade to Python 3.9 system-wide

```bash
# Install tflite-support (use version 0.4.3 to avoid GLIBCXX errors)
pip3 install --break-system-packages tflite-support==0.4.3 protobuf
```

**If you get GLIBCXX errors**, downgrade:
```bash
pip3 install --break-system-packages tflite-support==0.4.3
```

### 3. Run Object Detection

```bash
# Basic usage (default: 1280x720)
python3 object_detection.py

# Lower resolution for better performance
python3 object_detection.py --width 640 --height 480

# Adjust detection threshold (0.0-1.0, higher = more confident detections)
python3 object_detection.py --threshold 0.5

# Use EdgeTPU if you have Coral USB Accelerator
python3 object_detection.py --edgetpu
```

## Camera Module 3 Wide Configuration

The script is configured for **Camera Module 3 Wide** with:
- **102° horizontal FOV**
- Default resolution: 1280x720 (good balance of quality/performance)
- Supports up to 2304x1296 if needed

## Model Download

The script will automatically download the EfficientDet-Lite0 model on first run:
- **Default model**: `efficientdet_lite0.tflite` (~4MB)
- **EdgeTPU model**: `efficientdet_lite0_edgetpu.tflite` (if using `--edgetpu`)

Models are downloaded to the current directory.

## Performance Tips

1. **Lower resolution** = faster FPS:
   ```bash
   python3 object_detection.py --width 640 --height 480
   ```

2. **Adjust threads** (default: 4):
   ```bash
   python3 object_detection.py --threads 2  # Fewer threads
   python3 object_detection.py --threads 6  # More threads
   ```

3. **Limit detections** for better performance:
   ```bash
   python3 object_detection.py --max-results 2
   ```

4. **Use EdgeTPU** for 5-10x speedup (requires Coral USB Accelerator)

## Troubleshooting

### "tflite-support not installed"
```bash
pip3 install --break-system-packages tflite-support==0.4.3 protobuf
```

### "GLIBCXX_3.4.29 not found"
Downgrade tflite-support:
```bash
pip3 install --break-system-packages tflite-support==0.4.3
```

### "Python version not supported"
tflite-support requires Python 3.7-3.9. Check your version:
```bash
python3 --version
```

If you have Python 3.10+, create a virtual environment with Python 3.9 or downgrade your system Python.

### Camera not detected
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Install picamera2
sudo apt install python3-picamera2
```

### Low FPS
- Lower resolution: `--width 640 --height 480`
- Reduce max results: `--max-results 2`
- Increase threshold: `--threshold 0.5` (fewer detections to process)
- Use EdgeTPU if available

## Keyboard Controls

- **'q'** - Quit the program

## What Objects Can It Detect?

The EfficientDet-Lite0 model can detect 80 common objects including:
- Person, car, bicycle, motorcycle
- Cup, bottle, bowl
- Keyboard, mouse, laptop
- Chair, couch, bed
- Dog, cat, bird
- And many more!

See the terminal output for detected objects and their confidence scores.

