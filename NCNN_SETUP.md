# NCNN Model Setup Guide

This guide explains how to convert YOLO models to NCNN format for better performance on Raspberry Pi.

## What is NCNN?

NCNN is a high-performance neural network inference framework optimized for mobile and embedded platforms. It's specifically optimized for ARM architecture, making it ideal for Raspberry Pi devices.

**Benefits:**
- Faster inference on ARM CPUs
- Lower memory usage
- Better performance on Raspberry Pi compared to PyTorch models

Reference: [Ultralytics Raspberry Pi Guide](https://docs.ultralytics.com/guides/raspberry-pi/#use-ncnn-on-raspberry-pi)

## Quick Start

### 1. Convert Models to NCNN

Run the conversion script to convert all YOLO models to NCNN format:

```bash
python3 convert_to_ncnn.py
```

This will:
- Convert all models defined in `config.py` to NCNN format
- Create NCNN model directories (e.g., `yolo11n_ncnn_model/`)
- Provide instructions for updating config

### 2. Update Configuration

The `config.py` file has been updated to support NCNN models:

```python
USE_NCNN = True  # Set to False to use PyTorch models (.pt) instead

# Model paths automatically use NCNN if USE_NCNN=True
YOLO_MODEL = 'yolo11n_ncnn_model' if USE_NCNN else 'yolo11n.pt'
YOLO_POSE_MODEL = 'yolo11n-pose_ncnn_model' if USE_NCNN else 'yolo11n-pose.pt'
YOLO_OBB_MODEL = 'yolo11n-obb_ncnn_model' if USE_NCNN else 'yolo11n-obb.pt'
```

### 3. Automatic Fallback

The codebase has been updated to automatically fallback to PyTorch models if NCNN models are not found. This ensures:
- If NCNN model doesn't exist, it tries PyTorch version
- If PyTorch version doesn't exist, it downloads the default model
- No code changes needed - just run the conversion script

## Manual Conversion

If you need to convert a specific model manually:

```python
from ultralytics import YOLO

# Load PyTorch model
model = YOLO("yolo11n.pt")

# Export to NCNN format
model.export(format="ncnn")  # Creates 'yolo11n_ncnn_model' directory

# Load and use NCNN model
ncnn_model = YOLO("yolo11n_ncnn_model")
results = ncnn_model("image.jpg")
```

## Models Converted

The following models are automatically converted:

1. **YOLO_MODEL** (`yolo11n.pt`) → `yolo11n_ncnn_model/`
   - Used for: Object detection (home marker detection)

2. **YOLO_POSE_MODEL** (`yolo11n-pose.pt`) → `yolo11n-pose_ncnn_model/`
   - Used for: Pose estimation and person tracking

3. **YOLO_OBB_MODEL** (`yolo11n-obb.pt`) → `yolo11n-obb_ncnn_model/`
   - Used for: Oriented bounding box detection (trash detection)

4. **YOLO_CLOTHING_MODEL** (if exists) → `clothing_ncnn_model/`
   - Used for: RADD mode clothing detection

5. **YOLO_HAND_MODEL** (if exists) → `hand_keypoints_ncnn_model/`
   - Used for: Hand gesture recognition in manual mode

## Custom Trained Models

For custom trained models (e.g., clothing detection, hand keypoints):

1. Train your model as usual (saves as `.pt` file)
2. Convert to NCNN:
   ```python
   from ultralytics import YOLO
   model = YOLO("models/clothing/best.pt")
   model.export(format="ncnn", name="clothing_ncnn")
   ```
3. Update `config.py`:
   ```python
   YOLO_CLOTHING_MODEL = 'clothing_ncnn_model'  # or 'models/clothing/best.pt' for PyTorch
   ```

## Performance Comparison

According to Ultralytics benchmarks, NCNN models typically provide:
- **2-3x faster inference** on Raspberry Pi compared to PyTorch
- **Lower memory usage** (important for Raspberry Pi 4 with limited RAM)
- **Better CPU utilization** on ARM architecture

## Troubleshooting

### Model Not Found Error

If you see errors about NCNN models not being found:

1. **Check if models were converted:**
   ```bash
   ls -la | grep ncnn_model
   ```

2. **Re-run conversion:**
   ```bash
   python3 convert_to_ncnn.py
   ```

3. **Disable NCNN temporarily:**
   ```python
   # In config.py
   USE_NCNN = False
   ```

### Fallback to PyTorch

The code automatically falls back to PyTorch models if NCNN models fail to load. This is intentional and ensures the system continues to work even if NCNN conversion fails.

### Verify NCNN Model

Test if NCNN model loads correctly:

```python
from ultralytics import YOLO

# Try loading NCNN model
try:
    model = YOLO("yolo11n_ncnn_model")
    print("✓ NCNN model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load NCNN model: {e}")
```

## Files Updated

The following files have been updated to support NCNN with automatic fallback:

- `config.py` - Added `USE_NCNN` flag and NCNN model paths
- `main.py` - Home marker detection with NCNN fallback
- `test_yolo_pose_tracking.py` - Pose tracking with NCNN fallback
- `radd_detector.py` - Clothing detection with NCNN fallback
- `test_yolo_obb.py` - OBB detection with NCNN fallback
- `test_return.py` - Home marker detection with NCNN fallback
- `hand_gesture_controller.py` - Hand/pose models with NCNN fallback

## Next Steps

1. Run `python3 convert_to_ncnn.py` to convert all models
2. Test the system to ensure models load correctly
3. Monitor performance improvements
4. If issues occur, set `USE_NCNN = False` in `config.py` to revert to PyTorch

## References

- [Ultralytics Raspberry Pi Guide](https://docs.ultralytics.com/guides/raspberry-pi/#use-ncnn-on-raspberry-pi)
- [NCNN Export Documentation](https://docs.ultralytics.com/modes/export/#ncnn)

