#!/usr/bin/env python3
"""
System Check Script - Verifies everything is ready for multiple item detection
"""
import sys
import os
from pathlib import Path

def check_model():
    """Check if trained model exists and is loadable"""
    print("🔍 Checking Model...")
    backend_dir = Path(__file__).parent / 'backend'
    model_path = backend_dir / 'runs' / 'detect' / 'food_detector2' / 'weights' / 'best.pt'
    
    if not model_path.exists():
        print(f"  ❌ Trained model not found at {model_path}")
        return False
    
    print(f"  ✅ Model found: {model_path}")
    print(f"  📦 Size: {model_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        sys.path.insert(0, str(backend_dir))
        from vision_service import vision_service
        
        if not vision_service.is_ready:
            print("  ❌ Model failed to load")
            return False
        
        print(f"  ✅ Model loaded successfully")
        print(f"  🎯 Classes: {len(vision_service.names)}")
        
        # Show some sample classes
        sample_classes = list(vision_service.names.values())[:10]
        print(f"  📋 Sample classes: {', '.join(sample_classes[:5])}...")
        
        return True
    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies...")
    required = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS', 
        'ultralytics': 'Ultralytics',
        'PIL': 'Pillow',
        'numpy': 'NumPy'
    }
    
    all_good = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - Not installed")
            all_good = False
    
    return all_good

def check_frontend():
    """Check if frontend exists"""
    print("\n🎨 Checking Frontend...")
    frontend_dir = Path(__file__).parent / 'frontend'
    
    if not frontend_dir.exists():
        print("  ❌ Frontend directory not found")
        return False
    
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        print("  ❌ package.json not found")
        return False
    
    print("  ✅ Frontend directory found")
    print("  ✅ package.json exists")
    
    node_modules = frontend_dir / 'node_modules'
    if node_modules.exists():
        print("  ✅ node_modules installed")
    else:
        print("  ⚠️  node_modules not found - run 'npm install' in frontend/")
    
    return True

def main():
    print("=" * 60)
    print("🔧 Meal Plan App - System Check")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies()),
        ("Model", check_model()),
        ("Frontend", check_frontend())
    ]
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All systems ready!")
        print("\n🚀 To start the app:")
        print("   Backend:  cd backend && python3 app.py")
        print("   Frontend: cd frontend && npm run dev")
        print("\n📸 Upload images to detect multiple ingredients!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
    
    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
