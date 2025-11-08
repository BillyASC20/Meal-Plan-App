#!/usr/bin/env python3
"""
Test YOLOv8 detection with the trained model
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from vision_service import vision_service

def main():
    print("=" * 60)
    print("🧪 Testing YOLOv8 Ingredient Detection")
    print("=" * 60)
    
    if not vision_service.is_ready:
        print("❌ Model not loaded!")
        return
    
    print(f"✅ Model loaded successfully!")
    print(f"📊 Number of classes: {len(vision_service.names)}")
    print(f"\n🏷️  Sample classes:")
    sample_classes = list(vision_service.names.values())[:10]
    for i, cls in enumerate(sample_classes, 1):
        print(f"   {i}. {cls}")
    
    print(f"\n🔍 Total detectable items: {len(vision_service.names)}")
    print("=" * 60)
    print("\n✅ Vision service is ready for detection!")
    print("📸 Upload images through the frontend to test detection")
    print("=" * 60)

if __name__ == "__main__":
    main()
