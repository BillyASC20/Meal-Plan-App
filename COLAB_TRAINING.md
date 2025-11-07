# YOLOv8 Food Ingredient Detection - Google Colab Training
# Copy this entire file and paste into https://colab.research.google.com

## Step 1: Setup
```python
# Install required packages
!pip install -q ultralytics roboflow

# Import libraries
from ultralytics import YOLO
import os
from google.colab import files
import zipfile
```

## Step 2: Upload Your Dataset
```python
# Option A: Upload the Food-41 ZIP you downloaded from Kaggle
print("📤 Upload your food dataset ZIP file:")
uploaded = files.upload()

# Get the uploaded filename
zip_filename = list(uploaded.keys())[0]

# Extract it
!unzip -q {zip_filename}
print("✅ Dataset extracted!")
```

## Step 3: Prepare Dataset (Auto-convert to YOLO format)
```python
import shutil
from pathlib import Path
import random

def prepare_food_dataset():
    """Convert food classification dataset to YOLO format"""
    
    # Find the extracted folder
    folders = [f for f in os.listdir('.') if os.path.isdir(f) and f != 'sample_data']
    if not folders:
        print("❌ No dataset folder found!")
        return
    
    dataset_dir = Path(folders[0])  # Use first folder found
    print(f"📦 Using dataset: {dataset_dir}")
    
    # Create YOLO structure
    output_dir = Path('food-yolo')
    (output_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # Find all food classes
    train_dir = dataset_dir / 'train' if (dataset_dir / 'train').exists() else dataset_dir
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    
    print(f"📋 Found {len(classes)} food classes")
    
    # Process each class
    train_count = 0
    val_count = 0
    
    for idx, class_name in enumerate(classes):
        class_dir = train_dir / class_name
        images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
        
        if not images:
            continue
        
        # 80/20 split
        random.shuffle(images)
        split_idx = int(len(images) * 0.8)
        
        # Process images
        for img_path in images[:split_idx]:  # Train
            dest = output_dir / 'images' / 'train' / f"{class_name}_{img_path.name}"
            shutil.copy(img_path, dest)
            
            label = output_dir / 'labels' / 'train' / f"{class_name}_{img_path.stem}.txt"
            with open(label, 'w') as f:
                f.write(f"{idx} 0.5 0.5 1.0 1.0\n")
            train_count += 1
        
        for img_path in images[split_idx:]:  # Val
            dest = output_dir / 'images' / 'val' / f"{class_name}_{img_path.name}"
            shutil.copy(img_path, dest)
            
            label = output_dir / 'labels' / 'val' / f"{class_name}_{img_path.stem}.txt"
            with open(label, 'w') as f:
                f.write(f"{idx} 0.5 0.5 1.0 1.0\n")
            val_count += 1
        
        if idx % 5 == 0:
            print(f"   ✓ Processed {idx+1}/{len(classes)} classes...")
    
    # Create data.yaml
    yaml_content = f"""path: /content/food-yolo
train: images/train
val: images/val

nc: {len(classes)}
names: {classes}
"""
    
    with open(output_dir / 'data.yaml', 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Dataset ready! Train: {train_count}, Val: {val_count}")
    return str(output_dir / 'data.yaml')

# Run preparation
data_yaml = prepare_food_dataset()
```

## Step 4: Train on FREE GPU! 🚀
```python
# Load YOLOv8 nano model (fast and efficient)
model = YOLO('yolov8n.pt')

# Train with GPU acceleration
results = model.train(
    data=data_yaml,
    epochs=30,              # 30 epochs on GPU = ~15-20 minutes
    imgsz=640,
    batch=16,
    name='food_detector',
    device=0,               # Use GPU!
    patience=5,
    plots=True,
    verbose=True
)

print("\n🎉 Training complete!")
```

## Step 5: Download Your Trained Model
```python
# Download the best model
from google.colab import files

model_path = 'runs/detect/food_detector/weights/best.pt'
print(f"📥 Downloading trained model: {model_path}")

files.download(model_path)

print("✅ Downloaded! Rename it to 'ingredients.pt' and put in backend/models/")
```

## Step 6: Test It (Optional)
```python
# Test on a sample image
from PIL import Image
import requests
from io import BytesIO

# Load trained model
model = YOLO('runs/detect/food_detector/weights/best.pt')

# Upload test image
print("📤 Upload a test food image:")
uploaded = files.upload()
test_img = list(uploaded.keys())[0]

# Run detection
results = model(test_img)
results[0].show()  # Display results

print("\n✅ Detection results:")
for r in results:
    for box in r.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        name = model.names[cls]
        print(f"   {name}: {conf:.2f}")
```

---

## 🎯 **FULL INSTRUCTIONS:**

1. **Go to:** https://colab.research.google.com
2. **New Notebook** → Click "+ New notebook"
3. **Enable GPU:** Runtime → Change runtime type → T4 GPU → Save
4. **Copy/paste each code block** from above into cells
5. **Run cells** in order (click play button or Shift+Enter)
6. **Upload your ZIP** when prompted
7. **Wait 15-20 minutes** for training
8. **Download** the trained model (best.pt)
9. **Move to your project:** Rename to `ingredients.pt` and put in `backend/models/`

Done! 🎉

---

**Want me to create a ready-to-use Colab link you can just click and run?**
