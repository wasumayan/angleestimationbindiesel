#!/usr/bin/env python3
"""
Train YOLO hand-keypoints model
Trains a YOLO11n-pose model on the hand-keypoints dataset for gesture recognition

Reference: https://docs.ultralytics.com/datasets/pose/hand-keypoints/
"""

from ultralytics import YOLO

def train_hand_keypoints_model():
    """
    Train YOLO11n-pose model on hand-keypoints dataset
    
    The dataset will be automatically downloaded (369 MB, 26,768 images)
    Training will create: runs/pose/train/weights/best.pt
    """
    print("=" * 70)
    print("YOLO Hand Keypoints Model Training")
    print("=" * 70)
    print("Dataset: hand-keypoints (26,768 images, 21 keypoints per hand)")
    print("Model: yolo11n-pose.pt (nano - fastest)")
    print("Output: runs/pose/train/weights/best.pt")
    print()
    print("This will:")
    print("  1. Auto-download hand-keypoints dataset (369 MB)")
    print("  2. Train for 100 epochs")
    print("  3. Save best model as best.pt")
    print()
    print("=" * 70)
    print()
    
    # Load pretrained YOLO11n-pose model
    model = YOLO("yolo11n-pose.pt")
    
    # Train the model
    results = model.train(
        data="hand-keypoints.yaml",  # Dataset YAML (auto-downloads if not found)
        epochs=100,
        imgsz=640,
        batch=16,  # Adjust based on your GPU memory
        device=0,  # Use GPU 0, or 'cpu' for CPU training
        project="runs/pose",
        name="hand_keypoints",
        exist_ok=True
    )
    
    print()
    print("=" * 70)
    print("Training Complete!")
    print("=" * 70)
    print(f"Best model saved to: {results.save_dir}/weights/best.pt")
    print()
    print("To use the trained model:")
    print("  controller = HandGestureController(")
    print("      hand_model_path='runs/pose/hand_keypoints/weights/best.pt'")
    print("  )")
    print("=" * 70)


if __name__ == '__main__':
    train_hand_keypoints_model()

