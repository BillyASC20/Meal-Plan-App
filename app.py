import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from recipe_generator import RecipeGenerator

load_dotenv()

app = Flask(__name__)

recipe_gen = RecipeGenerator()

@app.route('/generate-recipes', methods=['GET'])
def generate_recipes():
    """Generate recipes endpoint."""
    try:
        result = recipe_gen.generate_recipes()
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
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)