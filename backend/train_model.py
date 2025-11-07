#!/usr/bin/env python3
"""
Train YOLOv8 model on Food-41 (or mini subset) with sensible defaults.

Environment overrides (optional):
  DATA_YAML  - path to data.yaml (default: datasets/food41-yolo/data.yaml)
  EPOCHS     - number of epochs (default: 50)
  IMGSZ      - image size (default: 320 for faster CPU runs)
  BATCH      - batch size (default: 16)
  DEVICE     - 'cuda' | 'mps' | 'cpu' (auto-detected if unset)

Usage:
    python train_model.py
"""

from ultralytics import YOLO
from pathlib import Path
import os
import torch

def train_food_model():
    """Train YOLOv8 on prepared food dataset."""
    
    # Resolve config from env (allow training on mini subset)
    data_yaml = Path(os.getenv('DATA_YAML', 'datasets/food41-yolo/data.yaml'))
    
    if not data_yaml.exists():
        print("❌ Dataset not prepared yet!")
        print("   Run: python prepare_dataset.py")
        return
    
    print("🚀 Starting YOLOv8 training on Food-41 dataset...")
    print("=" * 60)
    
    # Load a pre-trained model to fine-tune
    model = YOLO('yolov8n.pt')  # Nano model (fastest)
    
    # Hyperparams (speed-friendly defaults)
    epochs = int(os.getenv('EPOCHS', '50'))
    imgsz = int(os.getenv('IMGSZ', '320'))
    batch = int(os.getenv('BATCH', '16'))
    
    # Device selection: CUDA > MPS (Apple Silicon) > CPU
    device_env = os.getenv('DEVICE')
    if device_env:
        device = device_env
    else:
        if torch.cuda.is_available():
            device = 'cuda'
        elif getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    print(f"🖥️  Using device: {device}")
    
    # Train the model
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name='food_detector',  # Name for this training run
        patience=10,           # Early stopping patience
        save=True,             # Save checkpoints
        plots=True,            # Generate training plots
        device=device,
        workers=2,             # Keep low for laptop stability
        pretrained=True,       # Start from pre-trained weights
        optimizer='auto',      # Optimizer
        verbose=True,          # Verbose output
        seed=42,              # Random seed for reproducibility
    )
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"📊 Results saved to: runs/detect/food_detector/")
    print(f"🎯 Best model: runs/detect/food_detector/weights/best.pt")
    print("\n📝 Next steps:")
    print("   1. Copy best.pt to backend/models/ingredients.pt")
    print("   2. Restart your backend server or redeploy HF Space")
    print("   3. Upload food photos and test!")
    print("\n💡 To use the model:")
    print("   cp runs/detect/food_detector/weights/best.pt models/ingredients.pt")

if __name__ == "__main__":
    train_food_model()
