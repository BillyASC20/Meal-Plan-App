#!/usr/bin/env python3
"""
Script to prepare Food-41 dataset for YOLOv8 training.
Run this after unzipping the dataset.

Usage:
    python prepare_dataset.py
"""

import os
import shutil
from pathlib import Path
import random

def prepare_food41_for_yolo():
    """
    Convert Food-41 dataset to YOLOv8 format.
    
    Food-41 structure (classification):
    datasets/food41/
        ├── train/
        │   ├── class1/
        │   ├── class2/
        │   └── ...
        └── test/
    
    YOLOv8 needs (object detection):
    datasets/food41-yolo/
        ├── images/
        │   ├── train/
        │   └── val/
        ├── labels/
        │   ├── train/
        │   └── val/
        └── data.yaml
    """
    
    base_dir = Path(__file__).parent / 'datasets'
    food41_dir = base_dir / 'food41'  # Or whatever the extracted folder is named
    output_dir = base_dir / 'food41-yolo'
    
    # Check if source exists
    if not food41_dir.exists():
        print(f"❌ Food-41 dataset not found at: {food41_dir}")
        print(f"   Please unzip archive.zip in: {base_dir}")
        print(f"   Current files in datasets/:")
        if base_dir.exists():
            for item in base_dir.iterdir():
                print(f"   - {item.name}")
        return
    
    print(f"📦 Found Food-41 dataset at: {food41_dir}")
    print(f"🔨 Creating YOLOv8 format dataset at: {output_dir}")
    
    # Create output structure
    (output_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # Get all classes (food categories)
    train_dir = food41_dir / 'train' if (food41_dir / 'train').exists() else food41_dir / 'images'
    
    if not train_dir.exists():
        print(f"❌ Can't find train directory")
        print(f"   Listing {food41_dir}:")
        for item in food41_dir.iterdir():
            print(f"   - {item.name}")
        return
    
    classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
    classes.sort()
    
    print(f"📋 Found {len(classes)} food classes:")
    for i, cls in enumerate(classes[:10]):
        print(f"   {i}. {cls}")
    if len(classes) > 10:
        print(f"   ... and {len(classes) - 10} more")
    
    # Create class mapping
    class_to_id = {cls: idx for idx, cls in enumerate(classes)}
    
    # Process images
    total_images = 0
    train_count = 0
    val_count = 0
    
    for class_name in classes:
        class_dir = train_dir / class_name
        images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
        
        if not images:
            continue
        
        # Shuffle and split 80/20
        random.shuffle(images)
        split_idx = int(len(images) * 0.8)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        class_id = class_to_id[class_name]
        
        # Process train images
        for img_path in train_images:
            # Copy image
            dest_img = output_dir / 'images' / 'train' / f"{class_name}_{img_path.name}"
            shutil.copy(img_path, dest_img)
            
            # Create label (full image = one object)
            # Format: class_id center_x center_y width height (normalized 0-1)
            label_path = output_dir / 'labels' / 'train' / f"{class_name}_{img_path.stem}.txt"
            with open(label_path, 'w') as f:
                # Assume entire image is the food item (center of image, full size)
                f.write(f"{class_id} 0.5 0.5 1.0 1.0\n")
            
            train_count += 1
        
        # Process val images
        for img_path in val_images:
            dest_img = output_dir / 'images' / 'val' / f"{class_name}_{img_path.name}"
            shutil.copy(img_path, dest_img)
            
            label_path = output_dir / 'labels' / 'val' / f"{class_name}_{img_path.stem}.txt"
            with open(label_path, 'w') as f:
                f.write(f"{class_id} 0.5 0.5 1.0 1.0\n")
            
            val_count += 1
        
        total_images += len(images)
        print(f"   ✓ {class_name}: {len(train_images)} train, {len(val_images)} val")
    
    # Create data.yaml
    yaml_content = f"""# Food-41 Dataset for YOLOv8
path: {output_dir.absolute()}
train: images/train
val: images/val

# Classes
nc: {len(classes)}  # number of classes
names: {classes}  # class names
"""
    
    yaml_path = output_dir / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Dataset preparation complete!")
    print(f"   📊 Total images: {total_images}")
    print(f"   🎓 Training: {train_count}")
    print(f"   ✅ Validation: {val_count}")
    print(f"   📝 Config: {yaml_path}")
    print(f"\n🚀 Ready to train! Run:")
    print(f"   python train_model.py")

if __name__ == "__main__":
    prepare_food41_for_yolo()
