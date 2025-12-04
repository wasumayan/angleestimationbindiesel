# Object Detection Setup Guide

## Installation on Raspberry Pi

### 1. Pull Latest Changes
```bash
cd ~/angleestimationbindiesel  # or wherever your project is
git pull origin main
```

### 2. Install Ultralytics YOLO

**Much simpler than TensorFlow Lite!** YOLO works with any Python 3.6+ and doesn't have version conflicts.

```bash
# Install ultralytics (includes PyTorch and all dependencies)
pip3 install --break-system-packages ultralytics
```

That's it! No version conflicts, no Python version restrictions.

### 3. Run Object Detection

```bash
# Basic usage (default: 1280x720, yolo11n.pt model)
python3 object_detection.py

# Lower resolution for better performance
python3 object_detection.py --width 640 --height 480

# Adjust confidence threshold (0.0-1.0, higher = more confident detections)
python3 object_detection.py --conf 0.5

# Use a larger, more accurate model (slower but better detection)
python3 object_detection.py --model yolo11s.pt
```

## Camera Module 3 Wide Configuration

The script is configured for **Camera Module 3 Wide** with:
- **102° horizontal FOV**
- Default resolution: 1280x720 (good balance of quality/performance)
- Supports up to 2304x1296 if needed

## Model Download

The script will automatically download the YOLO model on first run:
- **Default model**: `yolo11n.pt` (nano) - ~6MB, fastest
- Models are downloaded to `~/.ultralytics/weights/` directory

### Available Models (from fastest to most accurate):

- `yolo11n.pt` (nano) - **Fastest**, least accurate - **Recommended for Pi**
- `yolo11s.pt` (small) - Balanced
- `yolo11m.pt` (medium) - Better accuracy
- `yolo11l.pt` (large) - High accuracy
- `yolo11x.pt` (extra large) - **Most accurate**, slowest

For Raspberry Pi, stick with `yolo11n.pt` or `yolo11s.pt` for real-time performance.

## Performance Tips

1. **Lower resolution** = faster FPS:
   ```bash
   python3 object_detection.py --width 640 --height 480
   ```

2. **Increase confidence threshold** to reduce false positives:
   ```bash
   python3 object_detection.py --conf 0.5
   ```

3. **Use nano model** (default) for best performance on Pi:
   ```bash
   python3 object_detection.py --model yolo11n.pt
   ```

4. **For better accuracy** (if you have Pi 4/5 with good cooling):
   ```bash
   python3 object_detection.py --model yolo11s.pt
   ```

## Troubleshooting

### "ultralytics not installed"
```bash
pip3 install --break-system-packages ultralytics
```

### "Model download failed"
The model downloads automatically. If it fails:
- Check internet connection
- Try running again (it will retry)
- Or manually download from: https://github.com/ultralytics/assets/releases

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
- Use nano model: `--model yolo11n.pt` (default)
- Increase confidence: `--conf 0.5` (fewer detections to process)
- Close other applications to free up CPU

### Out of memory
- Lower resolution: `--width 640 --height 480`
- Use nano model only: `--model yolo11n.pt`
- Close other applications

## Keyboard Controls

- **'q'** or **ESC** - Quit the program

## What Objects Can It Detect?

YOLO11 can detect 80 common objects including:
- Person, car, bicycle, motorcycle, bus, truck
- Cup, bottle, bowl, fork, knife, spoon
- Keyboard, mouse, laptop, cell phone
- Chair, couch, bed, dining table
- Dog, cat, bird, horse, cow, sheep
- And many more!

See the terminal output for detected objects and their confidence scores.

## Comparison: YOLO vs TensorFlow Lite

| Feature | YOLO (Ultralytics) | TensorFlow Lite |
|---------|-------------------|-----------------|
| Installation | Simple (`pip install ultralytics`) | Complex (version conflicts) |
| Python Support | 3.6+ | 3.7-3.9 only |
| Model Size | ~6MB (nano) | ~4MB |
| Accuracy | Excellent | Good |
| Speed | Fast | Fast |
| Ease of Use | Very Easy | Moderate |
| **Recommendation** | ✅ **Use this** | ❌ Avoid (version issues) |

## References

- Based on: https://github.com/automaticdai/rpi-object-detection
- Ultralytics YOLO Docs: https://docs.ultralytics.com/
- Raspberry Pi Guide: https://docs.ultralytics.com/guides/raspberry-pi/
