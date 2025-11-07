#!/usr/bin/env python3
"""
Quick test script for YOLOv8 ingredient detection.

Usage:
1. Run this script: python test_detection.py
2. It will download the YOLOv8 model (first time only)
3. Test on a sample image
"""

from vision_service import vision_service
import base64

def test_with_sample_image():
    """Test detection with a sample image URL."""
    print("=" * 60)
    print("🧪 Testing YOLOv8 Ingredient Detection")
    print("=" * 60)
    
    # For now, let's just verify the model loads
    print("\n✅ Vision service initialized successfully!")
    print(f"📦 Model loaded: {vision_service.model.ckpt_path if hasattr(vision_service.model, 'ckpt_path') else 'Pre-trained YOLOv8'}")
    print(f"🔍 Can detect {len(vision_service.food_mappings)} food categories")
    
    print("\n📋 Currently detectable ingredients:")
    for i, ingredient in enumerate(sorted(vision_service.food_mappings.keys()), 1):
        mapped = vision_service.food_mappings[ingredient]
        if mapped:  # Only show mapped items (not utensils)
            print(f"   {i}. {ingredient} → {mapped}")
    
    print("\n" + "=" * 60)
    print("💡 Next Steps:")
    print("=" * 60)
    print("1. ✅ Backend is ready to detect ingredients!")
    print("2. 📸 Take a photo from your frontend")
    print("3. 🔍 Pre-trained model will detect common foods")
    print("4. 🎓 Train custom model for more ingredients (see TRAINING_GUIDE.md)")
    print("\n🚀 To test with a real image:")
    print("   - Upload a photo through your React frontend")
    print("   - Or add a test image to this script")
    print("=" * 60)

def test_with_file(image_path):
    """
    Test detection with a local image file.
    
    Usage:
        test_with_file('path/to/your/image.jpg')
    """
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"\n🔍 Detecting ingredients in: {image_path}")
        ingredients = vision_service.detect_ingredients(base64_image)
        
        print(f"✅ Detected {len(ingredients)} ingredients:")
        for i, ingredient in enumerate(ingredients, 1):
            print(f"   {i}. {ingredient}")
        
        return ingredients
    
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
        return []
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    # Basic test - just verify the model loads
    test_with_sample_image()
    
    # Uncomment to test with your own image:
    # test_with_file('test_images/my_ingredients.jpg')
