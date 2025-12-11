# Model Training Guide

This guide covers training custom YOLO models for the Bin Diesel system.

## Overview

The system uses YOLO11 models for various tasks:
- **Pose Estimation**: `yolo11n-pose.pt` (pre-trained, no training needed)
- **Object Detection**: `yolo11n.pt` (pre-trained, no training needed)
- **Custom Models**: Hand keypoints, clothing detection (if needed)

## Training Custom Models

### Hand Keypoints Model

**Note:** Hand gesture control is currently commented out in the main system.

If you need to train a hand keypoints model:

1. **Prepare Dataset**: Use a hand keypoints dataset (e.g., from Ultralytics)
2. **Train on MacBook** (recommended - much faster than Raspberry Pi):

```bash
# Install dependencies
pip install ultralytics

# Run training script (if exists)
python train_hand_keypoints.py
```

**Training time estimates:**
- MacBook with M1/M2/M3 (GPU): ~30-60 minutes
- MacBook Intel (CPU): ~2-4 hours
- Raspberry Pi (CPU): ~8-12 hours (not recommended)

3. **Save Model**: Trained model should be saved to `models/hand_keypoints/weights/best.pt`

4. **Update Config**: Update `config.py`:
```python
YOLO_HAND_MODEL = 'models/hand_keypoints/weights/best.pt'
```

### Converting Models to NCNN

After training, convert models to NCNN format for better Raspberry Pi performance:

```bash
python3 convert_to_ncnn.py
```

This will convert all `.pt` models to NCNN format automatically.

## Model File Sizes

- Pre-trained YOLO models: ~6-12 MB each
- Custom trained models: ~5-10 MB typically
- NCNN models: Similar size, better performance on ARM

## Using Trained Models

1. **Place model in repository**: `models/your_model/weights/best.pt`
2. **Update config.py**: Set the model path
3. **Convert to NCNN** (optional but recommended):
   ```bash
   python3 convert_to_ncnn.py
   ```
4. **Commit and push**: Models are small enough to commit directly to git

## Training Tips

- **Use GPU when available**: Training on GPU is 10-20x faster
- **Start with fewer epochs**: Test with 20-50 epochs first
- **Use smaller models**: `yolo11n` is fastest, `yolo11s` is more accurate
- **Monitor training**: Watch for overfitting (validation loss increasing)

## References

- [Ultralytics Training Documentation](https://docs.ultralytics.com/modes/train/)
- [YOLO11 Model Zoo](https://docs.ultralytics.com/models/)
