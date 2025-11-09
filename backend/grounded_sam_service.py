
import base64
import io
import os
from pathlib import Path
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    from groundingdino.util.inference import Model as GroundingDINOModel
    from segment_anything import sam_model_registry, SamPredictor
    import torch
    import torchvision
    DEPENDENCIES_AVAILABLE = True
except Exception as e:
    print(f"[grounded_sam_service] Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


class GroundedSAMService:
    
    def __init__(self):
        self.is_ready = False
        self.grounding_dino_model = None
        self.sam_predictor = None
        
        self.food_categories = [
            "apple", "banana", "orange", "lemon", "lime", "strawberry", "blueberry",
            "grape", "watermelon", "melon", "pineapple", "mango", "peach", "pear",
            "cherry", "kiwi", "pomegranate", "plum", "apricot", "raspberry", "blackberry",
            "cantaloupe", "honeydew", "papaya", "passion fruit", "dragon fruit", "guava",
            "fig", "date", "cranberry", "grapefruit", "tangerine", "clementine", "mandarin",
            "coconut", "persimmon", "lychee", "star fruit", "kumquat", "nectarine",
            "tomato", "potato", "carrot", "broccoli", "lettuce", "cucumber", "pepper",
            "bell pepper", "onion", "garlic", "mushroom", "corn", "avocado", "pumpkin",
            "spinach", "cabbage", "eggplant", "zucchini", "squash", "celery", "radish",
            "cauliflower", "brussels sprouts", "asparagus", "artichoke", "beet", "turnip",
            "parsnip", "leek", "scallion", "green onion", "shallot", "ginger", "kale",
            "chard", "collard greens", "arugula", "bok choy", "fennel", "okra", "yam",
            "sweet potato", "green beans", "peas", "snap peas", "edamame", "bean sprouts",
            "jalapeno", "habanero", "chili pepper", "poblano", "serrano", "cayenne",
            "chicken", "chicken breast", "chicken thigh", "chicken wing", "whole chicken",
            "beef", "steak", "ribeye", "sirloin", "t-bone", "filet mignon", "brisket",
            "ground beef", "beef roast", "short ribs", "beef chuck", "flank steak",
            "pork", "pork chop", "pork loin", "pork belly", "pork ribs", "pork shoulder",
            "bacon", "sausage", "hot dog", "bratwurst", "chorizo", "salami", "pepperoni",
            "ham", "prosciutto", "pancetta", "canadian bacon", "turkey bacon",
            "turkey", "turkey breast", "ground turkey", "turkey leg", "whole turkey",
            "lamb", "lamb chop", "leg of lamb", "lamb shank", "ground lamb",
            "duck", "duck breast", "whole duck", "duck leg",
            "veal", "veal cutlet", "veal chop",
            "venison", "bison", "rabbit", "quail", "pheasant", "goose",
            "fish", "salmon", "tuna", "cod", "halibut", "tilapia", "trout", "bass",
            "catfish", "mahi mahi", "swordfish", "snapper", "grouper", "flounder",
            "mackerel", "sardine", "anchovy", "herring", "sea bass", "sole",
            "shrimp", "prawn", "crab", "lobster", "crayfish", "crawfish",
            "clam", "mussel", "oyster", "scallop", "squid", "calamari", "octopus",
            "milk", "whole milk", "skim milk", "almond milk", "soy milk", "oat milk",
            "cheese", "cheddar", "mozzarella", "parmesan", "swiss cheese", "brie",
            "feta", "goat cheese", "cream cheese", "blue cheese", "gouda", "provolone",
            "egg", "eggs", "egg white", "egg yolk",
            "butter", "margarine", "ghee",
            "yogurt", "greek yogurt", "sour cream", "cream", "heavy cream", "whipped cream",
            "cottage cheese", "ricotta", "mascarpone",
            "bread", "white bread", "wheat bread", "sourdough", "rye bread", "baguette",
            "pita", "naan", "tortilla", "wrap", "bagel", "english muffin", "croissant",
            "rice", "white rice", "brown rice", "wild rice", "jasmine rice", "basmati rice",
            "pasta", "spaghetti", "penne", "fettuccine", "linguine", "macaroni", "lasagna",
            "noodles", "ramen", "udon", "soba", "rice noodles", "egg noodles",
            "cereal", "oatmeal", "oats", "granola", "muesli",
            "flour", "wheat flour", "all purpose flour", "bread flour", "cake flour",
            "quinoa", "couscous", "bulgur", "farro", "barley", "millet",
            "pizza", "burger", "hamburger", "cheeseburger", "sandwich", "sub",
            "hot dog", "taco", "burrito", "quesadilla", "enchilada", "fajita",
            "salad", "caesar salad", "garden salad", "greek salad", "cobb salad",
            "soup", "stew", "chili", "curry", "casserole", "lasagna", "meatloaf",
            "cake", "chocolate cake", "vanilla cake", "cheesecake", "cupcake",
            "cookie", "chocolate chip cookie", "sugar cookie", "oatmeal cookie",
            "brownie", "blondie", "bar", "granola bar", "energy bar",
            "donut", "doughnut", "pie", "apple pie", "pumpkin pie", "pecan pie",
            "chocolate", "dark chocolate", "milk chocolate", "white chocolate",
            "candy", "gummy", "lollipop", "caramel", "toffee",
            "ice cream", "gelato", "sorbet", "frozen yogurt", "popsicle",
            "bottle", "can", "jar", "box", "package", "container", "bowl", "plate", "cup"
        ]
        
        self.box_threshold = 0.18  # Lower for more detections
        self.text_threshold = 0.18  # Lower for more detections
        
        if not DEPENDENCIES_AVAILABLE:
            print("[grounded_sam_service] Running in fallback mode (dependencies not available)")
            return
        
        try:
            self._load_models()
        except Exception as e:
            print(f"[grounded_sam_service] Failed to load models: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_models(self):
        backend_dir = Path(__file__).resolve().parent
        models_dir = backend_dir / "models" / "grounded_sam"
        
        import groundingdino
        grounding_dino_package_dir = Path(groundingdino.__file__).parent
        grounding_dino_config = grounding_dino_package_dir / "config" / "GroundingDINO_SwinT_OGC.py"
        grounding_dino_checkpoint = models_dir / "groundingdino_swint_ogc.pth"
        sam_checkpoint = models_dir / "sam_vit_b_01ec64.pth"  # Using base model (smaller, faster)
        
        repo_root = backend_dir.parent
        alt_grounding_checkpoint = repo_root / "groundingdino_swint_ogc.pth"
        alt_sam_checkpoint = repo_root / "sam_vit_h_4b8939.pth"
        
        if not grounding_dino_checkpoint.exists() and alt_grounding_checkpoint.exists():
            grounding_dino_checkpoint = alt_grounding_checkpoint
        if not sam_checkpoint.exists() and alt_sam_checkpoint.exists():
            sam_checkpoint = alt_sam_checkpoint
        
        if not grounding_dino_checkpoint.exists():
            print(f"[grounded_sam_service] ⚠️  Grounding DINO checkpoint not found at {grounding_dino_checkpoint}")
            print("[grounded_sam_service] Please download from: https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth")
            return
        
        if not sam_checkpoint.exists():
            print(f"[grounded_sam_service] ⚠️  SAM checkpoint not found at {sam_checkpoint}")
            print("[grounded_sam_service] Please download from: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth")
            return
        
        try:
            print(f"[grounded_sam_service] Loading Grounding DINO from {grounding_dino_checkpoint}")
            self.grounding_dino_model = GroundingDINOModel(
                model_config_path=str(grounding_dino_config),
                model_checkpoint_path=str(grounding_dino_checkpoint),
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            print("[grounded_sam_service] ✅ Grounding DINO loaded successfully")
        except Exception as e:
            print(f"[grounded_sam_service] Failed to load Grounding DINO: {e}")
            raise
        
        try:
            print(f"[grounded_sam_service] Loading SAM from {sam_checkpoint}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            sam = sam_model_registry["vit_b"](checkpoint=str(sam_checkpoint))
            sam.to(device=device)
            self.sam_predictor = SamPredictor(sam)
            print(f"[grounded_sam_service] ✅ SAM loaded successfully on {device}")
        except Exception as e:
            print(f"[grounded_sam_service] Failed to load SAM: {e}")
            raise
        
        self.is_ready = True
        print(f"[grounded_sam_service] 🎉 Service ready! Detecting {len(self.food_categories)} food categories")
    
    def _decode_image(self, base64_image):
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(data)).convert('RGB')
        return image
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union between two bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = box1["x1"], box1["y1"], box1["x2"], box1["y2"]
        x2_min, y2_min, x2_max, y2_max = box2["x1"], box2["y1"], box2["x2"], box2["y2"]
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def _create_text_prompt(self):
        essential_categories = [
            "apple", "banana", "orange", "lemon", "lime", "strawberry", "grape",
            "watermelon", "pineapple", "mango", "peach", "pear", "cherry", "kiwi",
            "blueberry", "raspberry", "blackberry", "avocado", "coconut", "grapefruit",
            "tomato", "potato", "carrot", "broccoli", "lettuce", "cucumber", "pepper",
            "onion", "garlic", "mushroom", "corn", "pumpkin", "spinach", "cabbage",
            "cauliflower", "celery", "zucchini", "eggplant", "asparagus", "green beans",
            "chicken", "beef", "pork", "fish", "salmon", "shrimp", "tuna", "turkey",
            "bacon", "sausage", "ham", "steak", "egg", "duck", "lamb",
            "milk", "cheese", "butter", "yogurt", "cream",
            "bread", "rice", "pasta", "noodles", "cereal", "tortilla",
            "pizza", "burger", "sandwich", "salad", "soup"
        ]
        return ". ".join(essential_categories) + "."
    
    def detect_with_confidence(self, base64_image, topk: int = 25):
        if not self.is_ready or self.grounding_dino_model is None:
            print("[grounded_sam_service] Model not ready, returning empty detections")
            return []
        
        try:
            pil_image = self._decode_image(base64_image)
            image_np = np.array(pil_image)
            
            text_prompt = self._create_text_prompt()
            
            detections, phrases = self.grounding_dino_model.predict_with_caption(
                image=image_np,
                caption=text_prompt,
                box_threshold=self.box_threshold,
                text_threshold=self.text_threshold
            )
            
            candidates = []
            
            if detections is not None and len(detections.xyxy) > 0:
                boxes = detections.xyxy
                confidences = detections.confidence
                
                for i in range(len(boxes)):
                    box = boxes[i]
                    confidence = float(confidences[i])
                    
                    phrase = phrases[i] if i < len(phrases) else "unknown"
                    
                    phrase_clean = phrase.lower().strip()
                    
                    special_char_count = sum(1 for c in phrase_clean if not c.isalnum() and c != ' ')
                    if special_char_count > 2 or len(phrase_clean) < 2:
                        print(f"[grounded_sam_service] Skipping noisy detection: '{phrase}'")
                        continue
                    
                    matched_name = None
                    best_match_score = 0
                    
                    for food_cat in self.food_categories:
                        if food_cat == phrase_clean:
                            matched_name = food_cat
                            best_match_score = 100
                            break
                        elif food_cat in phrase_clean:
                            score = len(food_cat) / len(phrase_clean)
                            if score > best_match_score:
                                matched_name = food_cat
                                best_match_score = score
                        elif phrase_clean in food_cat:
                            score = len(phrase_clean) / len(food_cat)
                            if score > best_match_score:
                                matched_name = food_cat
                                best_match_score = score
                    
                    if matched_name is None and best_match_score < 0.5:
                        if any(c.isalpha() for c in phrase_clean):
                            matched_name = phrase_clean
                        else:
                            print(f"[grounded_sam_service] Skipping non-food detection: '{phrase}'")
                            continue
                    
                    candidates.append({
                        "name": matched_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": float(box[0]),
                            "y1": float(box[1]),
                            "x2": float(box[2]),
                            "y2": float(box[3])
                        }
                    })
            
            candidates.sort(key=lambda x: x["confidence"], reverse=True)
            
            filtered = []
            for candidate in candidates:
                should_add = True
                for existing in filtered:
                    iou = self._calculate_iou(candidate["bbox"], existing["bbox"])
                    if iou > 0.5 and candidate["name"] == existing["name"]:
                        should_add = False
                        break
                    if iou > 0.7:
                        should_add = False
                        break
                
                if should_add:
                    filtered.append(candidate)
            
            seen = set()
            out = []
            for item in filtered:
                if item["name"] not in seen:
                    seen.add(item["name"])
                    out.append(item)
                if len(out) >= topk:
                    break
            
            print(f"[grounded_sam_service] Detected {len(out)} items: {[item['name'] + ' (' + str(round(item['confidence'], 2)) + ')' for item in out[:5]]}")
            return out
        
        except Exception as e:
            print(f"[grounded_sam_service] Detection error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def detect_multiple_items(self, base64_image, top_n_per_tile=2, grid_size=(3, 3), conf_threshold=0.1):
        return self.detect_with_confidence(base64_image, topk=8)
    
    def detect_ingredients(self, base64_image):
        preds = self.detect_with_confidence(base64_image, topk=8)
        return [p['name'] for p in preds]
    
    def detect_and_draw_boxes(self, base64_image, topk=25):
        if not self.is_ready or self.grounding_dino_model is None:
            print("[grounded_sam_service] Model not ready, returning original image")
            return {'image_with_boxes': base64_image, 'detections': []}
        
        try:
            pil_image = self._decode_image(base64_image)
            
            detections = self.detect_with_confidence(base64_image, topk=topk)
            
            draw = ImageDraw.Draw(pil_image)
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except:
                font = ImageFont.load_default()
            
            colors = ['lime', 'cyan', 'yellow', 'magenta', 'orange', 'pink']
            for idx, det in enumerate(detections):
                if 'bbox' not in det:
                    continue
                
                bbox = det['bbox']
                x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
                
                color = colors[idx % len(colors)]
                
                draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
                
                label = f"{det['name']} {det['confidence']:.0%}"
                
                bbox_text = draw.textbbox((x1, y1), label, font=font)
                text_width = bbox_text[2] - bbox_text[0]
                text_height = bbox_text[3] - bbox_text[1]
                
                draw.rectangle([x1, y1 - text_height - 8, x1 + text_width + 8, y1], fill=color)
                
                draw.text((x1 + 4, y1 - text_height - 4), label, fill='black', font=font)
            
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'image_with_boxes': f"data:image/jpeg;base64,{img_b64}",
                'detections': detections
            }
        
        except Exception as e:
            print(f"[grounded_sam_service] detect_and_draw_boxes error: {e}")
            import traceback
            traceback.print_exc()
            return {'image_with_boxes': base64_image, 'detections': []}


grounded_sam_service = GroundedSAMService()
