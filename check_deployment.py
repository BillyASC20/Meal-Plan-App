#!/usr/bin/env python3
"""
Quick verification that your model is ready for deployment.
Run this before deploying to check if everything works.
"""

import os
import sys
from pathlib import Path

def check_deployment_ready():
    """Check if deployment requirements are met."""
    
    print("=" * 60)
    print("🔍 Deployment Readiness Check")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # Check 1: Model file exists
    model_path = Path('backend/models/ingredients.pt')
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Model file found: {model_path}")
        print(f"   Size: {size_mb:.1f} MB")
        
        if size_mb < 1:
            warnings.append("⚠️  Model file is very small (<1 MB). Is it corrupted?")
        elif size_mb > 100:
            warnings.append("⚠️  Model file is large (>100 MB). Consider using a smaller model.")
    else:
        issues.append(f"❌ Model file NOT found: {model_path}")
        issues.append("   → Place your trained .pt file at backend/models/ingredients.pt")
    
    # Check 2: Backend files exist
    required_files = [
        'backend/app.py',
        'backend/vision_service.py',
        'backend/requirements.txt',
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            issues.append(f"❌ Missing required file: {file}")
    
    # Check 3: Check requirements.txt
    req_file = Path('backend/requirements.txt')
    if req_file.exists():
        content = req_file.read_text()
        if 'ultralytics' in content:
            print("✅ ultralytics in requirements.txt")
        else:
            issues.append("❌ ultralytics not in requirements.txt")
        
        if 'flask' in content:
            print("✅ flask in requirements.txt")
        else:
            issues.append("❌ flask not in requirements.txt")
    
    # Check 4: Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"✅ Python version: {py_version}")
    if sys.version_info.major < 3 or sys.version_info.minor < 8:
        warnings.append(f"⚠️  Python {py_version} detected. Recommended: 3.8+")
    
    # Summary
    print("\n" + "=" * 60)
    
    if issues:
        print("❌ DEPLOYMENT BLOCKED - Fix these issues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ ALL CHECKS PASSED!")
    
    if warnings:
        print("\n⚠️  Warnings (optional fixes):")
        for warning in warnings:
            print(f"   {warning}")
    
    print("=" * 60)
    
    if not issues:
        print("\n🚀 Ready to deploy!")
        print("\nNext steps:")
        print("1. Test locally: cd backend && python app.py")
        print("2. Deploy to HuggingFace/Railway/Render")
        print("3. Update frontend API URL")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_deployment_ready()
    sys.exit(0 if success else 1)
