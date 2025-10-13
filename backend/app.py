import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from recipe_generator import RecipeGenerator

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

recipe_gen = RecipeGenerator()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
    data = request.get_json() or {}
    ingredients = data.get('ingredients')

    if not ingredients:
        return jsonify({"status": "error", "message": "No ingredients provided"}), 400

    try:
        result = recipe_gen.generate_recipes(ingredients)
        return jsonify({"data": result})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)
