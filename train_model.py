"""
Train YOLOv8 on Food-101 Subset
"""
from ultralytics import YOLO

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting YOLOv8 Training on Food-101")
    print("=" * 60)
    print("📊 Training Configuration:")
    print("   - Model: YOLOv8n (nano)")
    print("   - Dataset: Food-101 Subset (~25k images, 101 classes)")
    print("   - Epochs: 100")
    print("   - Batch Size: 16")
    print("   - Device: GPU (CUDA)")
    print("=" * 60)

    # Load pretrained YOLOv8n model
    model = YOLO('yolov8n.pt')

    # Train
    results = model.train(
        data='datasets/food101-subset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,  # GPU
        patience=15,
        save=True,
        project='runs/detect',
        name='food101',
        exist_ok=True,
        verbose=True
    )

    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print(f"📁 Model saved to: runs/detect/food101/weights/best.pt")
    print("🎯 Copy best.pt to backend/models/ingredients.pt to use in app")
    print("=" * 60)
