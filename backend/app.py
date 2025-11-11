import os
import base64
import json
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from recipe_generator import RecipeGenerator
from pathlib import Path
from auth_middleware import require_auth

load_dotenv()

vision_service = None

try:
    from yolo_food_service import yolo_vision_service
    vision_service = yolo_vision_service
    print("[app] ✅ Using YOLOv8 food detector")
except Exception as e:
    print(f"[app] ❌ Failed to load YOLO detector: {e}")
    vision_service = None

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, resources={r"/*": {"origins": "*"}})

recipe_gen = RecipeGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
    "service": ("ready" if (vision_service and getattr(vision_service, 'is_ready', False)) else "loading")
    })

@app.route('/detect-ingredients', methods=['POST'])
@require_auth
def detect_ingredients():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No image data provided"}), 400

        image_data = data['image']
        print(f"[detect] Received image data, length: {len(image_data)}")
        
        if vision_service is None:
            return jsonify({"status": "error", "message": "Vision service unavailable"}), 500
        result = vision_service.detect_and_draw_boxes(image_data, topk=25)
        preds = result['detections']
        image_with_boxes = result['image_with_boxes']
        
        print(f"[detect] Got {len(preds)} predictions from vision service")
        print(f"[detect] Image with boxes length: {len(image_with_boxes) if image_with_boxes else 0}")
        
        if isinstance(preds, list) and len(preds) > 0:
            first = preds[0]
            if isinstance(first, dict):
                if "label" in first:
                    ingredients = [p["label"] for p in preds]
                else:
                    ingredients = [str(p) for p in preds]
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

        formatted_predictions = []
        for pred in preds:
            if isinstance(pred, dict):
                formatted_predictions.append({
                    "name": pred.get("label") or pred.get("name", "unknown"),
                    "confidence": pred.get("confidence", 0.0)
                })

        return jsonify({
            "status": "success",
            "data": {
                "ingredients": ingredients,
                "predictions": formatted_predictions,
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
@require_auth
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
@require_auth
def generate_recipes_stream():
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({
                "status": "error",
                "message": "No ingredients provided"
            }), 400
        
        ingredients = data['ingredients']
        image_url = data.get('image_url')
        
        auth_header = request.headers.get('Authorization')
        user_id = None
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from supabase import create_client
                supabase_url = os.getenv('SUPABASE_URL')
                supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                
                if supabase_url and supabase_key:
                    token = auth_header.replace('Bearer ', '')
                    supabase = create_client(supabase_url, supabase_key)
                    user = supabase.auth.get_user(token)
                    if user and user.user:
                        user_id = user.user.id
            except Exception as e:
                print(f"[stream] Could not get user: {e}")
        
        def generate():
            full_content = ""
            chunk_count = 0
            try:
                for chunk in recipe_gen.openai_service.generate_recipes_stream(ingredients):
                    full_content += chunk
                    chunk_count += 1
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                print(f"[stream] OpenAI streaming complete. Sent {chunk_count} chunks, total length: {len(full_content)}")
                
            except Exception as e:
                print(f"[stream] ❌ Error during streaming: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                return
            
            if user_id and image_url and full_content:
                try:
                    print(f"[stream] Stream finished, saving to database...")
                    print(f"[stream] User ID: {user_id}")
                    print(f"[stream] Image URL: {image_url}")
                    print(f"[stream] Content length: {len(full_content)} chars")
                    
                    import re
                    clean_json = full_content.strip()
                    clean_json = re.sub(r'^```json\s*', '', clean_json)
                    clean_json = re.sub(r'^```\s*', '', clean_json)
                    clean_json = re.sub(r'\s*```$', '', clean_json)
                    
                    print(f"[stream] Attempting to parse JSON...")
                    parsed_data = json.loads(clean_json)
                    recipes = parsed_data.get('recipes', [])
                    print(f"[stream] Found {len(recipes)} recipes")
                    
                    if recipes and len(recipes) > 0:
                        from supabase import create_client
                        supabase_url = os.getenv('SUPABASE_URL')
                        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                        
                        if not supabase_url or not supabase_key:
                            print(f"[stream] ❌ Supabase not configured!")
                        else:
                            supabase = create_client(supabase_url, supabase_key)
                            
                            print(f"[stream] Creating recipe_searches record...")
                            search_result = supabase.table('recipe_searches').insert({
                                'user_id': user_id,
                                'image_url': image_url,
                                'ingredients': ingredients
                            }).execute()
                            
                            search_id = search_result.data[0]['id']
                            print(f"[stream] Created search record: {search_id}")
                            
                            recipes_to_insert = []
                            for recipe in recipes:
                                recipes_to_insert.append({
                                    'search_id': search_id,
                                    'title': recipe.get('title'),
                                    'ingredients': recipe.get('ingredients'),
                                    'steps': recipe.get('steps'),
                                    'cooking_time': recipe.get('cookingTime') or recipe.get('cook_time'),
                                    'difficulty': recipe.get('difficulty'),
                                    'servings': str(recipe.get('servings', '')),
                                    'calories': recipe.get('calories')
                                })
                            
                            print(f"[stream] Inserting {len(recipes_to_insert)} recipes...")
                            supabase.table('recipes').insert(recipes_to_insert).execute()
                            print(f"[stream] ✅ Saved {len(recipes_to_insert)} recipes to database")
                    else:
                        print(f"[stream] ⚠️ No recipes found in parsed data")
                        
                except json.JSONDecodeError as json_error:
                    print(f"[stream] ❌ JSON parsing error: {json_error}")
                    print(f"[stream] First 500 chars: {full_content[:500]}")
                except Exception as save_error:
                    print(f"[stream] ❌ Error saving to database: {save_error}")
                    import traceback
                    traceback.print_exc()
            else:
                if not user_id:
                    print(f"[stream] ⚠️ No user_id - skipping save")
                if not image_url:
                    print(f"[stream] ⚠️ No image_url - skipping save")
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'
        response.headers['Connection'] = 'keep-alive'
        return response
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500


@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 400
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        return jsonify({
            "status": "success",
            "data": {
                "user": {
                    "id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else None
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/auth/signin', methods=['POST'])
def auth_signin():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 400
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return jsonify({
            "status": "success",
            "data": {
                "user": {
                    "id": response.user.id if response.user else None,
                    "email": response.user.email if response.user else None
                },
                "session": {
                    "access_token": response.session.access_token if response.session else None,
                    "refresh_token": response.session.refresh_token if response.session else None
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 401

@app.route('/auth/signout', methods=['POST'])
def auth_signout():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "No authorization token provided"
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        supabase.auth.sign_out()
        
        return jsonify({
            "status": "success",
            "message": "Signed out successfully"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/auth/reset-password', methods=['POST'])
def auth_reset_password():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email required"
            }), 400
        
        supabase.auth.reset_password_for_email(email)
        
        return jsonify({
            "status": "success",
            "message": "Password reset email sent"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/upload-image', methods=['POST'])
@require_auth
def upload_image():
    try:
        from supabase import create_client
        import uuid
        from datetime import datetime
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            return jsonify({
                "status": "error",
                "message": "Invalid token"
            }), 401
        
        user_id = user.user.id
        
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                "status": "error",
                "message": "Image data required"
            }), 400
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_id}/{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        
        result = supabase.storage.from_('Food Images').upload(
            path=filename,
            file=image_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        
        public_url = supabase.storage.from_('Food Images').get_public_url(filename)
        
        return jsonify({
            "status": "success",
            "data": {
                "image_url": public_url,
                "filename": filename
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/save-recipes', methods=['POST'])
@require_auth
def save_recipes():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            return jsonify({
                "status": "error",
                "message": "Invalid token"
            }), 401
        
        user_id = user.user.id
        
        data = request.get_json()
        image_url = data.get('image_url')
        ingredients = data.get('ingredients', [])
        recipes = data.get('recipes', [])
        
        if not image_url or not recipes:
            return jsonify({
                "status": "error",
                "message": "Image URL and recipes required"
            }), 400
        
        search_result = supabase.table('recipe_searches').insert({
            'user_id': user_id,
            'image_url': image_url,
            'ingredients': ingredients
        }).execute()
        
        search_id = search_result.data[0]['id']
        
        recipes_to_insert = []
        for recipe in recipes:
            recipes_to_insert.append({
                'search_id': search_id,
                'title': recipe.get('title'),
                'ingredients': recipe.get('ingredients'),
                'steps': recipe.get('steps'),
                'cooking_time': recipe.get('cookingTime'),
                'difficulty': recipe.get('difficulty'),
                'servings': recipe.get('servings'),
                'calories': recipe.get('calories')
            })
        
        supabase.table('recipes').insert(recipes_to_insert).execute()
        
        return jsonify({
            "status": "success",
            "data": {
                "search_id": search_id,
                "recipes_saved": len(recipes_to_insert)
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/recipe-history', methods=['GET'])
@require_auth
def get_recipe_history():
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            return jsonify({
                "status": "error",
                "message": "Invalid token"
            }), 401
        
        user_id = user.user.id
        
        print(f"[recipe-history] Fetching history for user: {user_id}")
        
        searches_result = supabase.table('recipe_searches')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        print(f"[recipe-history] Found {len(searches_result.data)} searches")
        
        searches_with_recipes = []
        
        for search in searches_result.data:
            recipes_result = supabase.table('recipes')\
                .select('*')\
                .eq('search_id', search['id'])\
                .order('created_at')\
                .execute()
            
            print(f"[recipe-history] Search {search['id']}: {len(recipes_result.data)} recipes")
            
            searches_with_recipes.append({
                'id': search['id'],
                'image_url': search['image_url'],
                'ingredients': search['ingredients'],
                'created_at': search['created_at'],
                'recipes': recipes_result.data
            })
        
        return jsonify({
            "status": "success",
            "data": searches_with_recipes
        })
        
    except Exception as e:
        print(f"[recipe-history] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/delete-recipe-search/<search_id>', methods=['DELETE', 'OPTIONS'])
def delete_recipe_search(search_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from supabase import create_client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                "status": "error",
                "message": "Supabase not configured on server"
            }), 500
        
        supabase = create_client(supabase_url, supabase_key)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            return jsonify({
                "status": "error",
                "message": "Invalid token"
            }), 401
        
        user_id = user.user.id
        
        print(f"[delete-search] User {user_id} deleting search {search_id}")
        
        search_result = supabase.table('recipe_searches').select('*').eq('id', search_id).eq('user_id', user_id).execute()
        
        if not search_result.data or len(search_result.data) == 0:
            return jsonify({
                "status": "error",
                "message": "Search not found or unauthorized"
            }), 404
        
        search = search_result.data[0]
        image_url = search['image_url']
        
        if 'Food%20Images' in image_url or 'Food Images' in image_url:
            if 'Food%20Images/' in image_url:
                file_path = image_url.split('Food%20Images/')[1]
            else:
                file_path = image_url.split('Food Images/')[1]
            
            import urllib.parse
            file_path = urllib.parse.unquote(file_path)
            
            print(f"[delete-search] Deleting S3 file: {file_path}")
            
            try:
                supabase.storage.from_('Food Images').remove([file_path])
                print(f"[delete-search] ✅ Deleted S3 file")
            except Exception as s3_error:
                print(f"[delete-search] ⚠️ S3 deletion failed: {s3_error}")
        
        supabase.table('recipe_searches').delete().eq('id', search_id).eq('user_id', user_id).execute()
        
        print(f"[delete-search] ✅ Deleted search and associated recipes")
        
        return jsonify({
            "status": "success",
            "message": "Recipe search deleted successfully"
        })
        
    except Exception as e:
        print(f"[delete-search] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def serve_frontend(path):
    if path.startswith('api/') or path.startswith('auth/') or path.startswith('detect-') or path.startswith('generate-') or path == 'health':
        return jsonify({"error": "Not found"}), 404
    
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)