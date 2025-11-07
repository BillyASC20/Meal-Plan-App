# YOLOv8 Training Guide for Ingredient Detection

This guide will help you train your own custom ingredient detector for FREE!

## 🎯 Overview

You'll be using **YOLOv8** (Ultralytics) - a state-of-the-art object detection model that you can train on your own images.

## 📋 Steps to Train Your Model

### Step 1: Collect Training Images

Gather 100-500+ images of ingredients you want to detect. More images = better accuracy.

**Tips:**
- Take photos from different angles
- Use different lighting conditions
- Include various backgrounds
- Mix single ingredients and combinations

**Example ingredients to train on:**
- Vegetables: broccoli, carrot, onion, garlic, potato, tomato, lettuce
- Proteins: chicken, beef, fish, eggs, tofu
- Grains: rice, pasta, bread, quinoa
- Fruits: apple, banana, orange, berries
- Dairy: milk, cheese, yogurt, butter

### Step 2: Label Your Images (FREE)

Use **Roboflow** (free tier) - the easiest way:

1. Go to [roboflow.com](https://roboflow.com) and create free account
2. Create new project: "Ingredient Detection"
3. Upload your images
4. Draw bounding boxes around each ingredient
5. Label each box (e.g., "chicken", "broccoli", "rice")
6. Export in **YOLOv8 format**

**Alternative tools:**
- LabelImg (desktop app, fully free)
- CVAT (free, open source)
- Makesense.ai (browser-based, free)

### Step 3: Organize Your Dataset

After exporting from Roboflow, organize like this:

```
backend/
├── datasets/
│   └── ingredients/
│       ├── data.yaml          # Dataset config (from Roboflow)
│       ├── train/
│       │   ├── images/        # Training images
│       │   └── labels/        # Training labels (.txt files)
│       └── val/
│           ├── images/        # Validation images
│           └── labels/        # Validation labels
└── models/                    # Where you'll save trained model
```

### Step 4: Train Your Model

Run this Python script in your backend folder:

```python
from vision_service import vision_service

# Train on your custom dataset
vision_service.train_custom_model(
    dataset_path='datasets/ingredients/data.yaml',
    epochs=50  # More epochs = better accuracy (but takes longer)
)
```

Or create a training script:

```python
# train_model.py
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8n.pt')  # nano model (fastest, good for CPU)

# Train on your ingredients
results = model.train(
    data='datasets/ingredients/data.yaml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='ingredient_detector',
    device='cpu'  # Use 'mps' for Mac GPU, 'cuda' for NVIDIA GPU
)

print("Training complete!")
print("Best model saved to: runs/detect/ingredient_detector/weights/best.pt")
```

Run it:
```bash
cd backend
python train_model.py
```

**Training time estimates:**
- CPU: 1-3 hours (for 50 epochs, 200 images)
- Mac M1/M2 GPU: 20-40 minutes
- NVIDIA GPU: 10-20 minutes

### Step 5: Use Your Trained Model

After training completes:

1. Copy the best model:
```bash
mkdir -p backend/models
cp runs/detect/ingredient_detector/weights/best.pt backend/models/ingredients.pt
```

2. Restart your Flask backend - it will automatically load your custom model!

The `vision_service.py` checks for `models/ingredients.pt` first, then falls back to the pre-trained model.

## 🚀 Quick Start (Using Pre-trained Model First)

Want to test it NOW before training? The pre-trained YOLOv8 can already detect some foods!

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run your Flask app:
```bash
python app.py
```

3. Take a photo with common objects (apple, banana, broccoli, carrot, etc.)

The pre-trained model knows 80 object classes including some food items!

## 📊 Model Performance Tips

**To improve accuracy:**
- Use more training images (300-500+ is ideal)
- Increase epochs (try 100 instead of 50)
- Use a larger model: `yolov8s.pt` or `yolov8m.pt` (slower but more accurate)
- Add data augmentation in Roboflow
- Include challenging images (overlapping ingredients, poor lighting)

**Model sizes:**
- `yolov8n.pt` - Nano (fastest, 3MB, good for mobile)
- `yolov8s.pt` - Small (better accuracy, 11MB)
- `yolov8m.pt` - Medium (best for most cases, 26MB)
- `yolov8l.pt` - Large (highest accuracy, 44MB)

## 🎓 Free Resources

**Datasets to practice with:**
- [Open Images Dataset](https://storage.googleapis.com/openimages/web/index.html) - has food categories
- [Food-101 Dataset](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) - 101 food categories
- [Kaggle Food Datasets](https://www.kaggle.com/search?q=food+detection) - many free options

**Tutorials:**
- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com)
- [Roboflow Blog](https://blog.roboflow.com) - excellent tutorials
- [Custom YOLOv8 Training Tutorial](https://blog.roboflow.com/how-to-train-yolov8-on-a-custom-dataset/)

## 💡 Pro Tips

1. **Start small**: Train on 5-10 common ingredients first, then expand
2. **Test continuously**: Test your model on new images after every training session
3. **Iterate**: Retrain with more images of ingredients it struggles with
4. **Use augmentation**: Roboflow can auto-generate variations (flips, crops, brightness changes)
5. **Balance your dataset**: Have similar numbers of images for each ingredient

## 🔧 Troubleshooting

**"Model detects nothing":**
- Lower confidence threshold in `vision_service.py` (change `conf=0.25` to `conf=0.15`)
- Check if objects are labeled correctly
- Try taking clearer photos with better lighting

**"Training is too slow":**
- Use fewer epochs (try 30)
- Use smaller model (yolov8n.pt)
- Use smaller image size (imgsz=416 instead of 640)
- Reduce batch size (batch=8 or batch=4)

**"Not enough memory":**
- Reduce batch size
- Use smaller model
- Close other applications

## 🎉 You're All Set!

This approach is:
- ✅ **100% FREE** (no API costs)
- ✅ **Self-hosted** (runs on your computer)
- ✅ **Customizable** (train on YOUR ingredients)
- ✅ **Fast** (real-time detection once trained)
- ✅ **Privacy-friendly** (images never leave your computer)

Good luck with your senior project! 🚀
