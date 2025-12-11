#!/usr/bin/env python3
"""
Convert YOLO models to NCNN format for Raspberry Pi optimization
NCNN is optimized for ARM architecture and provides better performance on Raspberry Pi

Reference: https://docs.ultralytics.com/guides/raspberry-pi/#use-ncnn-on-raspberry-pi
"""

import os
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not installed!")
    print("Install with: pip install ultralytics")
    sys.exit(1)

import config


def convert_model(model_path, output_name=None):
    """
    Convert a YOLO model to NCNN format
    
    Args:
        model_path: Path to PyTorch model (.pt file)
        output_name: Optional output directory name (default: auto-generated)
    
    Returns:
        Path to converted NCNN model directory
    """
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found: {model_path}")
        return None
    
    print(f"\n{'='*70}")
    print(f"Converting: {model_path}")
    print(f"{'='*70}")
    
    try:
        # Load PyTorch model
        print(f"[1/3] Loading PyTorch model: {model_path}...")
        model = YOLO(model_path)
        print(f"      ✓ Model loaded successfully")
        
        # Export to NCNN format
        print(f"[2/3] Exporting to NCNN format...")
        if output_name:
            exported_path = model.export(format="ncnn", name=output_name)
        else:
            exported_path = model.export(format="ncnn")
        print(f"      ✓ Model exported to: {exported_path}")
        
        # Verify NCNN model can be loaded
        print(f"[3/3] Verifying NCNN model...")
        ncnn_model = YOLO(exported_path)
        print(f"      ✓ NCNN model verified and ready to use")
        
        return exported_path
        
    except Exception as e:
        print(f"      ✗ ERROR: Failed to convert {model_path}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Convert all models used in the system to NCNN format"""
    print("="*70)
    print("YOLO to NCNN Model Converter")
    print("="*70)
    print("This script converts all YOLO models to NCNN format for")
    print("better performance on Raspberry Pi (ARM architecture)")
    print("="*70)
    print()
    
    models_to_convert = []
    
    # Standard models - use .pt files for conversion (will auto-download if needed)
    # These are the base model names that YOLO will download if not found
    models_to_convert.append(('YOLO_MODEL', 'yolo11n.pt', 'yolo11n_ncnn'))
    models_to_convert.append(('YOLO_POSE_MODEL', 'yolo11n-pose.pt', 'yolo11n-pose_ncnn'))
    models_to_convert.append(('YOLO_OBB_MODEL', 'yolo11n-obb.pt', 'yolo11n-obb_ncnn'))
    
    # Custom trained models
    if hasattr(config, 'YOLO_CLOTHING_MODEL') and config.YOLO_CLOTHING_MODEL:
        if os.path.exists(config.YOLO_CLOTHING_MODEL):
            models_to_convert.append(('YOLO_CLOTHING_MODEL', config.YOLO_CLOTHING_MODEL, 'clothing_ncnn'))
        else:
            print(f"WARNING: YOLO_CLOTHING_MODEL not found: {config.YOLO_CLOTHING_MODEL}")
    
    if hasattr(config, 'YOLO_HAND_MODEL') and config.YOLO_HAND_MODEL:
        if os.path.exists(config.YOLO_HAND_MODEL):
            models_to_convert.append(('YOLO_HAND_MODEL', config.YOLO_HAND_MODEL, 'hand_keypoints_ncnn'))
        else:
            print(f"WARNING: YOLO_HAND_MODEL not found: {config.YOLO_HAND_MODEL}")
    
    if not models_to_convert:
        print("No models to convert!")
        return
    
    print(f"Found {len(models_to_convert)} model(s) to convert:")
    for name, path, _ in models_to_convert:
        print(f"  - {name}: {path}")
    print()
    
    converted_models = {}
    
    for model_name, model_path, output_name in models_to_convert:
        # Check if model exists (auto-download models will be handled by YOLO)
        if not os.path.exists(model_path) and not model_path.startswith('yolo11'):
            print(f"\nSKIPPING {model_name}: File not found: {model_path}")
            continue
        
        ncnn_path = convert_model(model_path, output_name)
        if ncnn_path:
            converted_models[model_name] = ncnn_path
    
    # Summary
    print("\n" + "="*70)
    print("Conversion Summary")
    print("="*70)
    
    if converted_models:
        print("\n✓ Successfully converted models:")
        for model_name, ncnn_path in converted_models.items():
            print(f"  {model_name}:")
            print(f"    Original: {getattr(config, model_name, 'N/A')}")
            print(f"    NCNN:     {ncnn_path}")
        
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("1. Update config.py to use NCNN model paths:")
        print("   Example:")
        for model_name, ncnn_path in converted_models.items():
            print(f"   {model_name} = '{ncnn_path}'")
        print("\n2. Test the models to ensure they work correctly")
        print("3. NCNN models should provide better performance on Raspberry Pi")
    else:
        print("\n✗ No models were successfully converted")
    
    print("="*70)


if __name__ == '__main__':
    main()

