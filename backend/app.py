import os
import base64
import json
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv
from recipe_generator import RecipeGenerator
from pathlib import Path

load_dotenv()

from grounded_sam_service import grounded_sam_service as vision_service

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

recipe_gen = RecipeGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ready" if vision_service.is_ready else "loading"
    })

@app.route('/detect-ingredients', methods=['POST'])
def detect_ingredients():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No image data provided"}), 400

        image_data = data['image']
        print(f"[detect] Received image data, length: {len(image_data)}")
        
        result = vision_service.detect_and_draw_boxes(image_data, topk=25)
        preds = result['detections']
        image_with_boxes = result['image_with_boxes']
        
        print(f"[detect] Got {len(preds)} predictions from vision service")
        print(f"[detect] Image with boxes length: {len(image_with_boxes) if image_with_boxes else 0}")
        
        if isinstance(preds, list) and len(preds) > 0:
            first = preds[0]
            if isinstance(first, dict) and "name" in first:
                ingredients = [p["name"] for p in preds]
            else:
                ingredients = [str(p) for p in preds]
        else:
            ingredients = []

        message = None
        if not ingredients:
            message = "nothing_detected"
            print("[detect] ⚠️  No ingredients detected!")
        else:
            print(f"[detect] ✅ Returning {len(ingredients)} ingredients: {ingredients[:5]}")

        return jsonify({
            "status": "success",
            "data": {
                "ingredients": ingredients,
                "predictions": preds,
                "image_with_boxes": image_with_boxes,
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

@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
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

@app.route('/generate-recipes-stream', methods=['POST'])
def generate_recipes_stream():
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({
                "status": "error",
                "message": "No ingredients provided"
            }), 400
        
        ingredients = data['ingredients']
        
        def generate():
            try:
                for chunk in recipe_gen.openai_service.generate_recipes_stream(ingredients):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)