import io
import base64
import os
import time
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class YOLOFoodDetector:
    
    DEFAULT_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
    DEFAULT_FONT_PATHS = [
        "/System/Library/Fonts/Helvetica.ttc",  
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  
        "C:\\Windows\\Fonts\\arial.ttf"  
    ]
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.is_ready = False
        self.model = None
        self._font = None
        
        print(f"[yolo] Initializing YOLOv8 detector with model: {self.model_path}")
        
        try:
            from ultralytics import YOLO
            
            start_time = time.time()
            self.model = YOLO(self.model_path)
            load_time = time.time() - start_time
            
            self.is_ready = True
            print(f"[yolo] ✅ Model loaded successfully in {load_time:.2f}s")
            print(f"[yolo] Model classes: {len(self.model.names)} categories")
            
        except Exception as e:
            print(f"[yolo] Failed to load model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}") from e

    def detect_and_draw_boxes(
        self,
        image_data: str,
        topk: int = 25,
        score_thresh: float = 0.35
    ) -> Dict[str, any]:
        if not self.is_ready or not self.model:
            raise RuntimeError("Model not initialized")
        if not image_data or not isinstance(image_data, str):
            raise ValueError("Invalid image data: must be non-empty string")
        if not 0.0 <= score_thresh <= 1.0:
            raise ValueError(f"Invalid threshold: {score_thresh} (must be 0.0-1.0)")
        if topk < 1 or topk > 100:
            raise ValueError(f"Invalid topk: {topk} (must be 1-100)")
        try:
            if ',' in image_data:
                image_data = image_data.split(',', 1)[1]
            image_bytes = base64.b64decode(image_data)
            if len(image_bytes) > self.MAX_IMAGE_SIZE:
                raise ValueError(f"Image too large: {len(image_bytes)} bytes (max {self.MAX_IMAGE_SIZE})")
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            start_time = time.time()
            results = self.model(image, conf=score_thresh, verbose=False)
            inference_time = time.time() - start_time
            detected_labels = set()
            detections = []
            for result in results:
                boxes = result.boxes
                for i, box in enumerate(boxes):
                    conf = float(box.conf[0])
                    if conf < score_thresh:
                        continue
                    cls = int(box.cls[0])
                    class_name = result.names[cls]
                    if class_name.lower() not in detected_labels:
                        detected_labels.add(class_name.lower())
                        detections.append(class_name)
                    if len(detections) >= topk:
                        break
            print(f"[yolo] Inference completed in {inference_time:.3f}s. Detected: {detections}")
            return {
                'items': detections
            }
        except Exception as e:
            print(f"[yolo] Detection error: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Detection failed: {e}") from e

    def _draw_boxes(self, image: Image.Image, detections: List[Dict], high_thresh: float = 0.35) -> Image.Image:
        draw = ImageDraw.Draw(image)
        font = self._get_font()

        for det in detections:
            bbox = det['bbox']
            label = det['label']
            conf = det['confidence']

            box_color = '#10B981'
            bg_color = '#10B981'

            draw.rectangle(bbox, outline=box_color, width=4)

            label_text = f"{label} ({conf:.2f})"

            try:
                left, top, right, bottom = draw.textbbox((bbox[0], bbox[1]), label_text, font=font)
                text_width = right - left
                text_height = bottom - top
            except AttributeError:
                text_width, text_height = draw.textsize(label_text, font=font)

            draw.rectangle(
                [bbox[0], bbox[1] - text_height - 4, bbox[0] + text_width + 4, bbox[1]],
                fill=bg_color
            )

            draw.text((bbox[0] + 2, bbox[1] - text_height - 2), label_text, fill='white', font=font)

        print(f"[yolo] _draw_boxes: Drew {len(detections)} boxes (single color)")
        return image
    
    def _get_font(self, size: int = 20) -> ImageFont.ImageFont:
        if self._font is not None:
            return self._font
        
        for font_path in self.DEFAULT_FONT_PATHS:
            try:
                self._font = ImageFont.truetype(font_path, size)
                return self._font
            except (OSError, IOError):
                continue
        
        self._font = ImageFont.load_default()
        return self._font

    def _image_to_data_url(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=90)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"


try:
    yolo_vision_service = YOLOFoodDetector()
except Exception as e:
    print(f"[yolo] Failed to initialize: {e}")
    yolo_vision_service = None
