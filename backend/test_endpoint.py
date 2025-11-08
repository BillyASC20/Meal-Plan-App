#!/usr/bin/env python3
"""Quick test to see if detection is working"""
import requests
import json

# Test with sample endpoint
print("Testing backend endpoints...")
print("=" * 60)

# Test 1: Sample detections
try:
    response = requests.get('http://127.0.0.1:5000/debug/sample-detections')
    print("✅ Sample detections endpoint:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Sample detections failed: {e}")

print("\n" + "=" * 60)

# Test 2: Get hero image and detect
try:
    print("Testing real detection with hero image...")
    hero_response = requests.get('http://127.0.0.1:5000/debug/hero-b64')
    hero_data = hero_response.json()
    
    if hero_data['status'] == 'success':
        image_data = hero_data['data']['image']
        print(f"✅ Got hero image (length: {len(image_data)} chars)")
        
        # Now detect
        detect_response = requests.post(
            'http://127.0.0.1:5000/detect-ingredients',
            json={'image': image_data},
            headers={'Content-Type': 'application/json'}
        )
        
        result = detect_response.json()
        print("\n🔍 Detection result:")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            data = result['data']
            print(f"Ingredients found: {len(data.get('ingredients', []))}")
            print(f"Predictions: {len(data.get('predictions', []))}")
            if data.get('predictions'):
                print("\nTop detections:")
                for pred in data['predictions'][:5]:
                    print(f"  - {pred['name']}: {pred['confidence']:.2%}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            
except Exception as e:
    print(f"❌ Detection test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
