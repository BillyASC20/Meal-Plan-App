"""
Download Food-101 Dataset from HuggingFace (Subset: ~25k images)
Samples ~250 images per class across ALL 101 food classes
"""

import os
import random
from datasets import load_dataset
from pathlib import Path
from PIL import Image
import yaml
from tqdm import tqdm

print("=" * 60)
print("📦 Downloading Food-101 Dataset (Subset)")
print("=" * 60)
print("📊 Dataset Info:")
print("   - Source: HuggingFace (ethz/food101)")
print("   - Total Images: ~25,000 (subset)")
print("   - Classes: 101 food types")
print("   - Sampling: ~250 images per class (balanced)")
print("   - Training time on RTX 3070: ~5-7 hours")
print("=" * 60)

# Configuration
IMAGES_PER_CLASS = 250  # ~250 per class = ~25k total
TRAIN_SPLIT = 0.8  # 80% train, 20% validation
OUTPUT_DIR = Path("datasets/food101-subset")

print(f"\n⏳ Loading Food-101 dataset from HuggingFace...")
print("   (First time may take 10-20 minutes to download)")

try:
    # Load dataset - simple approach
    ds = load_dataset("ethz/food101")
    dataset = ds
    
    # Get class names
    class_names = dataset['train'].features['label'].names
    num_classes = len(class_names)
    
    print(f"\n✅ Dataset loaded!")
    print(f"   Classes: {num_classes}")
    print(f"   Class names: {', '.join(class_names[:5])}... (and {num_classes-5} more)")
    
    # Create output directories
    train_images_dir = OUTPUT_DIR / "train" / "images"
    train_labels_dir = OUTPUT_DIR / "train" / "labels"
    val_images_dir = OUTPUT_DIR / "valid" / "images"
    val_labels_dir = OUTPUT_DIR / "valid" / "labels"
    
    for dir in [train_images_dir, train_labels_dir, val_images_dir, val_labels_dir]:
        dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🔄 Sampling {IMAGES_PER_CLASS} images per class...")
    
    # Group images by class
    train_data = dataset['train']
    val_data = dataset['validation']
    
    # Combine train and validation for resampling
    all_images_by_class = {i: [] for i in range(num_classes)}
    
    for split, data in [('train', train_data), ('val', val_data)]:
        for idx, item in enumerate(data):
            label = item['label']
            all_images_by_class[label].append(item)
    
    # Sample balanced subset with RANDOMIZATION for better distribution
    print(f"\n🎲 Randomizing selection for quality diversity...")
    random.seed(42)  # Set seed for reproducibility
    
    sampled_images = []
    for class_id in range(num_classes):
        class_images = all_images_by_class[class_id]
        
        # RANDOMIZE: shuffle and sample from different parts of dataset
        random.shuffle(class_images)
        sample_size = min(len(class_images), IMAGES_PER_CLASS)
        sampled = class_images[:sample_size]
        
        for img_data in sampled:
            sampled_images.append({
                'image': img_data['image'],
                'label': class_id,
                'class_name': class_names[class_id]
            })
    
    # Shuffle and split into train/val
    random.shuffle(sampled_images)
    split_idx = int(len(sampled_images) * TRAIN_SPLIT)
    train_samples = sampled_images[:split_idx]
    val_samples = sampled_images[split_idx:]
    
    print(f"   Total sampled: {len(sampled_images)} images")
    print(f"   Train: {len(train_samples)} images")
    print(f"   Validation: {len(val_samples)} images")
    
    # Save images and labels in YOLO format
    def save_samples(samples, img_dir, lbl_dir, split_name):
        print(f"\n💾 Saving {split_name} set...")
        for idx, sample in enumerate(tqdm(samples, desc=f"  {split_name}")):
            # Save image
            img_path = img_dir / f"{idx:06d}.jpg"
            sample['image'].convert('RGB').save(img_path, 'JPEG')
            
            # Save label (YOLO classification format: just class_id)
            # For object detection, we'd need bounding boxes
            # For now, save as classification label
            lbl_path = lbl_dir / f"{idx:06d}.txt"
            with open(lbl_path, 'w') as f:
                # YOLO format for whole image classification
                # Format: class_id x_center y_center width height (normalized)
                # For full image: 0.5 0.5 1.0 1.0
                f.write(f"{sample['label']} 0.5 0.5 1.0 1.0\n")
    
    save_samples(train_samples, train_images_dir, train_labels_dir, "train")
    save_samples(val_samples, val_images_dir, val_labels_dir, "validation")
    
    # Create data.yaml for YOLO
    data_yaml = {
        'path': str(OUTPUT_DIR.absolute()),
        'train': 'train/images',
        'val': 'valid/images',
        'nc': num_classes,
        'names': class_names
    }
    
    yaml_path = OUTPUT_DIR / "data.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Food-101 subset downloaded!")
    print("=" * 60)
    print(f"📁 Location: {OUTPUT_DIR.absolute()}")
    print(f"📊 Classes: {num_classes}")
    print(f"📸 Total images: {len(sampled_images)}")
    print(f"   Train: {len(train_samples)}")
    print(f"   Validation: {len(val_samples)}")
    print(f"\n📋 Class list:")
    for i, name in enumerate(class_names[:10]):
        print(f"   {i}: {name}")
    print(f"   ... and {num_classes-10} more")
    
    print("\n🚀 Ready to train!")
    print("   Next step: python train_model.py")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ Missing dependency: {e}")
    print("\n💡 Install required packages:")
    print("   pip install datasets pillow pyyaml tqdm")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Make sure you have internet connection")
    print("   2. Install dependencies: pip install datasets pillow pyyaml tqdm")
    print("   3. HuggingFace may require login for some datasets")
    
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Dataset downloaded!")
    print("=" * 60)
    print(f"📁 Location: {dataset.location}")
    print(f"📊 Classes detected:")
    
    # Read data.yaml to show classes
    import yaml
    yaml_path = f"{dataset.location}/data.yaml"
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            classes = data.get('names', [])
            print(f"   Total: {len(classes)} classes")
            print(f"   {', '.join(classes[:10])}...")
    except:
        print("   (Classes info in data.yaml)")
    
    print("\n🚀 Ready to train!")
    print("   Next step: python train_model.py")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check your API key is correct")
    print("   2. Make sure you have internet connection")
    print("   3. Install roboflow: pip install roboflow")
