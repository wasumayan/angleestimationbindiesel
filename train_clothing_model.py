"""
Train YOLO Clothing Detection Model
Based on: https://github.com/kesimeg/YOLO-Clothing-Detection

This script trains a YOLO model to detect clothing items:
- accessories (class 0)
- bags (class 1)
- clothing (class 2)
- shoes (class 3)
"""

from ultralytics import YOLO
import argparse
import yaml
import os

def main():
    parser = argparse.ArgumentParser(description="YOLO Clothing Detection Training Script")
    parser.add_argument("--epochs", type=int, default=30, help="Number of epochs (default: 30)")
    parser.add_argument("--patience", type=int, default=5, help="Patience for early stopping (default: 5)")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size (default: 64)")
    parser.add_argument("--model_name", type=str, default="yolo11n.pt", 
                       help="Pretrained model to finetune (default: yolov8n.pt)")
    parser.add_argument("--data_dir", type=str, default="datasets/fashion_dataset",
                       help="Path to dataset directory (default: datasets/fashion_dataset)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for training (default: 640)")
    parser.add_argument("--device", type=str, default=None, 
                       help="Device to use (default: auto-detect GPU/CPU)")
    
    args = parser.parse_args()
    
    # Check if dataset exists
    if not os.path.exists(args.data_dir):
        print(f"ERROR: Dataset directory not found: {args.data_dir}")
        print("\nTo prepare the dataset, run:")
        print("  1. Clone: git clone https://github.com/kesimeg/YOLO-Clothing-Detection.git")
        print("  2. Run: python data_preprocessing.py")
        print("  3. Copy datasets/fashion_dataset to this project")
        return
    
    # Create data.yaml configuration
    # Based on official repo: classes are ["accessories","bags","clothing","shoes"]
    data_config = {
        'path': os.path.abspath(args.data_dir),  # Absolute path to dataset
        'train': 'train/images',  # Relative to path
        'val': 'val/images',      # Relative to path
        'nc': 4,  # Number of classes
        'names': ["accessories", "bags", "clothing", "shoes"]  # Class names in order
    }
    
    # Save data.yaml in dataset directory
    data_yaml_path = os.path.join(args.data_dir, 'data.yaml')
    with open(data_yaml_path, 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print(f"Data configuration saved to: {data_yaml_path}")
    print(f"Classes: {data_config['names']}")
    print(f"Class indices: 0=accessories, 1=bags, 2=clothing, 3=shoes")
    
    # Load YOLO model
    print(f"\nLoading model: {args.model_name}")
    try:
        model = YOLO(args.model_name)  # Will auto-download if not found
    except Exception as e:
        print(f"ERROR: Failed to load model {args.model_name}: {e}")
        print("Trying default: yolo11n.pt")
        model = YOLO('yolo11n.pt')
    
    # Train the model
    print(f"\nStarting training...")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Patience: {args.patience}")
    print(f"  Image size: {args.imgsz}")
    print(f"  Device: {args.device or 'auto'}")
    
    try:
        results = model.train(
            data=data_yaml_path,
            epochs=args.epochs,
            batch=args.batch_size,
            patience=args.patience,
            imgsz=args.imgsz,
            device=args.device,
            project='runs/clothing',  # Save to runs/clothing/
            name='train',             # Subdirectory name
            exist_ok=True,            # Overwrite if exists
            verbose=True
        )
        
        print("\n" + "="*60)
        print("Training completed!")
        print("="*60)
        
        # Find the best model path
        # YOLO saves to: runs/clothing/train/weights/best.pt
        best_model_path = os.path.join('runs', 'clothing', 'train', 'weights', 'best.pt')
        if os.path.exists(best_model_path):
            print(f"\nBest model saved to: {best_model_path}")
            print(f"\nTo use this model, update config.py:")
            print(f"  YOLO_CLOTHING_MODEL = '{best_model_path}'")
            
            # Also suggest copying to models directory
            models_dir = 'models/clothing'
            os.makedirs(models_dir, exist_ok=True)
            import shutil
            shutil.copy(best_model_path, os.path.join(models_dir, 'best.pt'))
            print(f"\nModel also copied to: {os.path.join(models_dir, 'best.pt')}")
            print(f"  YOLO_CLOTHING_MODEL = 'models/clothing/best.pt'")
        else:
            print(f"\nWARNING: Best model not found at expected path: {best_model_path}")
            print("Check runs/clothing/train/weights/ for model files")
        
    except Exception as e:
        print(f"\nERROR: Training failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nTraining script completed!")


if __name__ == '__main__':
    main()

