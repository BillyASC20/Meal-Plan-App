import os
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from .recipe_generator import RecipeGenerator
from .vision_service import vision_service
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for frontend communication
CORS(app)

# Initialize the recipe generator
recipe_gen = RecipeGenerator()

@app.route('/detect-ingredients', methods=['POST'])
def detect_ingredients():
    """Detect ingredients from uploaded image using OpenAI Vision."""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No image data provided"}), 400

        image_data = data['image']
        # Use local model; prefer the helper that accepts base64 and returns
        # multiple predictions with confidences.
        # detect_with_confidence handles tiling, detection/classification heads
        # and returns a list like [{"name": str, "confidence": float}, ...]
        preds = vision_service.detect_with_confidence(image_data, topk=8)

        # Normalize ingredients: if preds is a list of dicts, pull 'name',
        # otherwise if it's a list of strings use it directly.
        if isinstance(preds, list) and len(preds) > 0:
            first = preds[0]
            if isinstance(first, dict) and "name" in first:
                ingredients = [p["name"] for p in preds]
            else:
                # assume list of strings
                ingredients = [str(p) for p in preds]
        else:
            # If model isn't ready (failed to load) return a helpful sample
            # so frontend can be tested immediately.
            if not getattr(vision_service, 'is_ready', True):
                sample_preds = [
                    {"name": "apple", "confidence": 0.92},
                    {"name": "banana", "confidence": 0.81},
                    {"name": "broccoli", "confidence": 0.66},
                ]
                preds = sample_preds
                ingredients = [p["name"] for p in preds]
            else:
                ingredients = []

        message = None
        if not ingredients:
            message = "nothing_detected"

        return jsonify({
            "status": "success",
            "data": {
                "ingredients": ingredients,
                "predictions": preds,
                **({"message": message} if message else {})
            }
        })
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/debug/hero-b64', methods=['GET'])
def debug_hero_b64():
    """Return the hero AVIF image as a data URL for easy frontend testing."""
    try:
        # repo root = parent of backend directory
        repo_root = Path(__file__).resolve().parent.parent
        hero_path = repo_root / 'fridge-hero-mobile.avif'
        if not hero_path.exists():
            return jsonify({"status": "error", "message": "hero image not found"}), 404
        data = hero_path.read_bytes()
        b64 = base64.b64encode(data).decode('utf-8')
        data_url = f"data:image/avif;base64,{b64}"
        return jsonify({"status": "success", "data": {"image": data_url}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/debug/sample-detections', methods=['GET'])
def debug_sample_detections():
    """Return a canned multi-item detection result for frontend testing."""
    sample_preds = [
        {"name": "apple", "confidence": 0.92},
        {"name": "banana", "confidence": 0.81},
        {"name": "broccoli", "confidence": 0.66},
    ]
    ingredients = [p["name"] for p in sample_preds]
    return jsonify({
        "status": "success",
        "data": {
            "ingredients": ingredients,
            "predictions": sample_preds
        }
    })

@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
    """Generate recipes from detected ingredients."""
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({
                "status": "error",
                "message": "No ingredients provided"
            }), 400
        
        ingredients = data['ingredients']
        result = recipe_gen.generate_recipes(ingredients)
        
        return jsonify({
            "status": "success",
            "data": result
        })
    
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Use environment variables for configuration, with sensible defaults
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)