# Clothing Model Training & Usage Fixes

## Issues Found and Fixed

After comparing our implementation with the [official YOLO-Clothing-Detection repository](https://github.com/kesimeg/YOLO-Clothing-Detection), we identified and fixed several issues:

### 1. **Class Index Mismatch** ✅ FIXED

**Problem**: We had incorrect class indices hardcoded:
```python
# WRONG (old code):
self.clothing_classes = {
    'clothing': 0,  # ❌ Wrong!
    'shoes': 1,     # ❌ Wrong!
    'bags': 2,      # ❌ Wrong!
    'accessories': 3  # ❌ Wrong!
}
```

**Official Repository** (from `model_training.py`):
```python
'names': ["accessories", "bags", "clothing", "shoes"]
# Class indices:
#   0: accessories
#   1: bags
#   2: clothing
#   3: shoes
```

**Fix**: Changed to dynamically read class names from the model:
```python
# ✅ FIXED (new code):
# Dynamically map classes from model.names
# Uses actual class names from trained model (more reliable)
```

### 2. **Training Configuration** ✅ FIXED

**Problem**: We didn't have a proper training script matching the official repo's configuration.

**Official Repository Settings**:
- `epochs`: 30 (default)
- `patience`: 5 (early stopping)
- `batch_size`: 64
- `imgsz`: 640
- Data format: YOLO format with `data.yaml`

**Fix**: Created `train_clothing_model.py` that:
- Matches official training configuration
- Creates proper `data.yaml` with correct class order
- Uses correct paths and settings
- Auto-saves model to `runs/clothing/train/weights/best.pt`

### 3. **Model Inference Settings** ✅ FIXED

**Problem**: We weren't using consistent image size during inference.

**Fix**: Added `imgsz=640` to match training image size:
```python
results = self.model(
    person_roi,
    conf=self.confidence,
    verbose=False,
    imgsz=640  # ✅ Match training image size
)
```

### 4. **Class Detection Logic** ✅ IMPROVED

**Problem**: Using fragile string matching for class detection.

**Fix**: 
- Primary: Use class indices from model mapping
- Fallback: String matching (for compatibility)
- More robust and reliable

## How to Train the Model Correctly

### Step 1: Prepare Dataset

```bash
# Clone the official repository
git clone https://github.com/kesimeg/YOLO-Clothing-Detection.git
cd YOLO-Clothing-Detection

# Run data preprocessing (downloads and converts dataset)
python data_preprocessing.py

# This creates: datasets/fashion_dataset/
#   - train/images/ and train/labels/
#   - val/images/ and val/labels/
#   - test/images/ and test/labels/
```

### Step 2: Copy Dataset to Project

```bash
# From YOLO-Clothing-Detection directory
cp -r datasets/fashion_dataset /path/to/bindiesel/datasets/
```

### Step 3: Train Using Our Script

```bash
# From bindiesel directory
python train_clothing_model.py \
    --epochs 30 \
    --batch_size 64 \
    --patience 5 \
    --model_name yolo11n.pt \
    --data_dir datasets/fashion_dataset \
    --imgsz 640
```

**Or use defaults**:
```bash
python train_clothing_model.py
```

### Step 4: Update Config

After training, the model will be saved to:
- `runs/clothing/train/weights/best.pt` (training output)
- `models/clothing/best.pt` (auto-copied)

Update `config.py`:
```python
YOLO_CLOTHING_MODEL = 'models/clothing/best.pt'
```

## Training Parameters (Official Settings)

Based on [official model_training.py](https://raw.githubusercontent.com/kesimeg/YOLO-Clothing-Detection/main/model_training.py):

| Parameter | Official Value | Our Default | Notes |
|-----------|---------------|-------------|-------|
| `epochs` | 30 | 30 | Number of training epochs |
| `patience` | 5 | 5 | Early stopping patience |
| `batch_size` | 64 | 64 | Batch size for training |
| `imgsz` | 640 | 640 | Image size (must match inference) |
| `model_name` | yolov8n.pt | yolo11n.pt | Base model (updated to YOLO11) |

## Class Order (IMPORTANT!)

The official repository uses this class order:
```python
names = ["accessories", "bags", "clothing", "shoes"]
```

**Class Indices**:
- `0`: accessories
- `1`: bags
- `2`: clothing
- `3`: shoes

**Our code now automatically detects this from the model**, so it works correctly regardless of training order.

## Dataset Structure

After preprocessing, the dataset should look like:
```
datasets/
└── fashion_dataset/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
```

## Verification

After training, verify the model works:

```python
from radd_detector import RADDDetector
import cv2

# Load detector
detector = RADDDetector(model_path='models/clothing/best.pt')

# Test on image
frame = cv2.imread('test_image.jpg')
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Detect violations
result, yolo_result = detector._detect_violation_with_model(frame_rgb, None)
print(f"Violations: {result}")
print(f"Model classes: {detector.model.names}")
print(f"Mapped classes: {detector.clothing_classes}")
```

## Performance Tips

1. **Use GPU if available**: Training is much faster on GPU
   ```bash
   python train_clothing_model.py --device 0  # Use GPU 0
   ```

2. **Adjust batch size**: If you run out of memory, reduce batch size
   ```bash
   python train_clothing_model.py --batch_size 32
   ```

3. **Monitor training**: Check `runs/clothing/train/` for:
   - Training curves
   - Validation metrics
   - Best model weights

## Summary of Changes

1. ✅ Fixed class index mapping (now uses model.names dynamically)
2. ✅ Created proper training script matching official repo
3. ✅ Added consistent image size (640) for inference
4. ✅ Improved class detection logic (more robust)
5. ✅ Auto-copy trained model to `models/clothing/`

## References

- Official Repository: https://github.com/kesimeg/YOLO-Clothing-Detection
- Training Script: https://raw.githubusercontent.com/kesimeg/YOLO-Clothing-Detection/main/model_training.py
- Data Preprocessing: https://raw.githubusercontent.com/kesimeg/YOLO-Clothing-Detection/main/data_preprocessing.py
- Dataset: https://huggingface.co/datasets/detection-datasets/fashionpedia_4_categories

