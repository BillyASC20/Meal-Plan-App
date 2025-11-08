
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
            "tomato", "potato", "carrot", "broccoli", "lettuce", "cucumber", "pepper",
            "onion", "garlic", "mushroom", "corn", "avocado", "pumpkin",
            "bread", "cheese", "milk", "egg", "butter", "yogurt",
            "chicken", "beef", "pork", "fish", "salmon", "shrimp",
            "rice", "pasta", "noodles", "cereal",
            "pizza", "burger", "sandwich", "hot dog", "taco",
            "cake", "cookie", "donut", "pie", "chocolate",
            "bottle", "can", "jar", "box", "package", "container"
        ]
        
        self.box_threshold = 0.15
        self.text_threshold = 0.15
        
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
        
        grounding_dino_config = backend_dir / "GroundingDINO" / "groundingdino" / "config" / "GroundingDINO_SwinT_OGC.py"
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
    
    def _create_text_prompt(self):
        return ". ".join(self.food_categories) + "."
    
    def detect_with_confidence(self, base64_image, topk: int = 25):
        if not self.is_ready or self.grounding_dino_model is None:
            print("[grounded_sam_service] Model not ready, returning empty detections")
            return []
        
        try:
            pil_image = self._decode_image(base64_image)
            image_np = np.array(pil_image)
            
            text_prompt = self._create_text_prompt()
            
            detections = self.grounding_dino_model.predict_with_classes(
                image=image_np,
                classes=self.food_categories,
                box_threshold=self.box_threshold,
                text_threshold=self.text_threshold
            )
            
            candidates = []
            
            if detections is not None and len(detections.xyxy) > 0:
                boxes = detections.xyxy
                confidences = detections.confidence
                class_ids = detections.class_id
                
                for i in range(len(boxes)):
                    box = boxes[i]
                    confidence = float(confidences[i])
                    class_id = int(class_ids[i])
                    class_name = self.food_categories[class_id]
                    
                    candidates.append({
                        "name": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": float(box[0]),
                            "y1": float(box[1]),
                            "x2": float(box[2]),
                            "y2": float(box[3])
                        }
                    })
            
            candidates.sort(key=lambda x: x["confidence"], reverse=True)
            seen = set()
            out = []
            for item in candidates:
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
