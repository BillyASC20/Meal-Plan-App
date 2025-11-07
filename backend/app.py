import os
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from recipe_generator import RecipeGenerator

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
        # Get image data from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                "status": "error",
                "message": "No image data provided"
            }), 400
        
        # Extract base64 image data
        image_data = data['image']
        
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Detect ingredients using OpenAI Vision
        ingredients = recipe_gen.detect_ingredients_from_image(image_data)
        
        return jsonify({
            "status": "success",
            "data": {
                "ingredients": ingredients
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