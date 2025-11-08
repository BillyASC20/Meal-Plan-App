import base64
import io
import os
from pathlib import Path

# Try to import heavy deps; if they fail, we'll run in "no-model" fallback mode.
try:
    from ultralytics import YOLO
    from PIL import Image
    import numpy as np
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


class VisionService:
    """Lightweight vision service wrapper.

    - If torch/ultralytics model is available, loads the model and performs
      inference with tiling to harvest multiple detections.
    - Otherwise returns empty lists (safe fallback) so the server can run.
    """

    def __init__(self):
        self.is_ready = False
        self.model = None
        self.names = {}
        self.food_mappings = {
            'apple': 'apple',
            'banana': 'banana',
            'orange': 'orange',
            'broccoli': 'broccoli',
            'carrot': 'carrot',
            'hot dog': 'hot dog',
            'pizza': 'pizza',
            'donut': 'donut',
            'cake': 'cake',
            'sandwich': 'sandwich',
            'bottle': 'beverage',
            'wine glass': 'wine',
            'cup': 'beverage',
            'bowl': 'bowl',
            'knife': None,
            'fork': None,
            'spoon': None,
        }

        if not TORCH_AVAILABLE:
            print("[vision_service] ultralytics/PIL/numpy not available. Running in fallback mode.")
            return

        try:
            # Prefer a custom model in backend/models/ingredients.pt if present
            # Or use the trained model from runs/detect
            repo_dir = Path(__file__).resolve().parent
            
            # Try trained model first, then fall back to ingredients.pt
            trained_model = repo_dir / 'runs' / 'detect' / 'food_detector2' / 'weights' / 'best.pt'
            default_model = repo_dir / 'models' / 'ingredients.pt'
            
            if trained_model.exists():
                model_path = str(trained_model)
            elif default_model.exists():
                model_path = str(default_model)
            else:
                model_path = os.getenv('YOLO_MODEL_PATH')
            
            if not model_path or not os.path.exists(model_path):
                print(f"[vision_service] Model not found at {model_path}.")
                print("[vision_service] No model loaded — fallback detections will be used.")
                self.model = None
                self.is_ready = False
                return

            # Load YOLOv8 model using ultralytics
            try:
                self.model = YOLO(model_path)
                # names mapping
                self.names = self.model.names or {}
                self.is_ready = True
                print(f"[vision_service] YOLOv8 model loaded successfully from {model_path}")
                print(f"[vision_service] Can detect {len(self.names)} classes.")
            except Exception as load_err:
                print(f"[vision_service] Failed to load model from {model_path}: {load_err}")
                print("[vision_service] Fallback detections will be used.")
                self.model = None
                self.is_ready = False

        except Exception as e:
            print(f"[vision_service] Unexpected error during init: {e}")
            self.model = None
            self.is_ready = False

    def _decode_image(self, base64_image):
        # Accept data URLs or raw base64 strings
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(data)).convert('RGB')
        return image

    def _split_tiles(self, pil_image, grid_size=(3, 3)):
        w, h = pil_image.size
        tiles = []
        tile_w = max(1, w // grid_size[0])
        tile_h = max(1, h // grid_size[1])
        for gy in range(grid_size[1]):
            for gx in range(grid_size[0]):
                left = gx * tile_w
                upper = gy * tile_h
                right = left + tile_w if (gx < grid_size[0] - 1) else w
                lower = upper + tile_h if (gy < grid_size[1] - 1) else h
                tile = pil_image.crop((left, upper, right, lower))
                tiles.append(tile)
        return tiles

    def detect_with_confidence(self, base64_image, topk: int = 25):
        """Return list of {name, confidence} detected from base64 image.

        If model isn't available, returns empty list.
        """
        if not self.is_ready or self.model is None:
            return []

        try:
            pil_image = self._decode_image(base64_image)

            # YOLOv8 detection - start with VERY low confidence for grocery photos
            results = self.model(pil_image, conf=0.01, verbose=False)  # Changed from 0.15 to 0.01
            
            candidates = []
            
            # Extract detections from results with bounding boxes
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        try:
                            class_id = int(box.cls[0].item())
                            class_name = self.names.get(class_id, str(class_id))
                            confidence = float(box.conf[0].item())
                            
                            # Get bounding box coordinates (xyxy format: x1, y1, x2, y2)
                            bbox = box.xyxy[0].cpu().numpy().tolist()
                            
                            candidates.append({
                                "name": class_name,
                                "confidence": confidence,
                                "bbox": {
                                    "x1": float(bbox[0]),
                                    "y1": float(bbox[1]),
                                    "x2": float(bbox[2]),
                                    "y2": float(bbox[3])
                                }
                            })
                        except Exception as e:
                            print(f"[vision_service] Error processing box: {e}")
                            continue

            # Sort by confidence and remove duplicates
            candidates.sort(key=lambda x: x["confidence"], reverse=True)
            seen = set()
            out = []
            for item in candidates:
                if item["name"] not in seen:
                    seen.add(item["name"])
                    out.append(item)
                if len(out) >= topk:
                    break

            print(f"[vision_service] Detected {len(out)} items: {[item['name'] + ' (' + str(round(item['confidence'], 2)) + ')' for item in out[:5]]}")
            return out
            
        except Exception as e:
            print(f"[vision_service] detect error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def detect_multiple_items(self, base64_image, top_n_per_tile=2, grid_size=(3, 3), conf_threshold=0.1):
        """Backward-compatible wrapper that returns list of {name, confidence}.

        This mirrors older helper names used elsewhere in the codebase.
        """
        preds = self.detect_with_confidence(base64_image, topk=8)
        return preds

    def detect_ingredients(self, base64_image):
        """Return a simple list of ingredient names (strings).

        This is used by older callers that expect a list of strings.
        """
        preds = self.detect_with_confidence(base64_image, topk=8)
        return [p['name'] for p in preds]


# singleton
vision_service = VisionService()
