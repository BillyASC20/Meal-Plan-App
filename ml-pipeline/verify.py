#!/usr/bin/env python3
"""
Quick verification script to test the ML pipeline without training.
Tests rule-based classification only.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("ML PIPELINE VERIFICATION")
print("=" * 60)

print("\n1. Testing imports...")
try:
    from health_rules import classify_ingredient_health_risk, analyze_recipe_risks
    from feature_engineering import IngredientFeatureExtractor
    from health_risk_service import get_health_risk_service
    print("   ✅ All modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

print("\n2. Testing rule-based classification...")
try:
    test_ingredients = ["butter", "spinach", "bacon", "olive oil"]
    for ing in test_ingredients:
        risks = classify_ingredient_health_risk(ing)
        print(f"   ✓ Classified: {ing}")
    print("   ✅ Rule-based classification working")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n3. Testing feature extraction...")
try:
    extractor = IngredientFeatureExtractor()
    features = extractor.extract_features("cheddar cheese")
    print(f"   ✓ Extracted {len(features)} features")
    print("   ✅ Feature extraction working")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n4. Testing recipe analysis...")
try:
    recipe = ["butter", "cheese", "bacon", "eggs", "spinach"]
    analysis = analyze_recipe_risks(recipe)
    print(f"   ✓ Overall risk: {analysis['overall_risk']}")
    print(f"   ✓ Warnings: {len(analysis['warnings'])}")
    print("   ✅ Recipe analysis working")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n5. Testing service initialization...")
try:
    service = get_health_risk_service()
    summary = service.get_risk_summary(["butter", "olive oil"])
    print(f"   ✓ Service initialized")
    print(f"   ✓ Risk summary generated")
    print("   ✅ Service working")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED")
print("=" * 60)
print("\nThe ML pipeline is correctly installed!")
print("\nNext steps:")
print("  1. Place CSV files in data/ directory")
print("  2. Run: python cli.py train")
print("  3. Test: python cli.py predict -i 'cheese,butter'")
print("\nOr use rule-based classification immediately:")
print("  python cli.py analyze -i 'spinach,chicken,rice'")
print("  python examples.py")
