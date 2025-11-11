import io
import base64
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class YOLOFoodDetector:
    def __init__(self):
        print("[yolo] Loading YOLOv8 food-specific model...")
        self.is_ready = False
        
        try:
            from ultralytics import YOLO
            
            try:
                print("[yolo] Attempting to load YOLOv8m (medium) for better accuracy...")
                self.model = YOLO('yolov8m.pt')
                print("[yolo] ✅ Loaded YOLOv8m (medium) - better accuracy than nano")
            except Exception as e:
                print(f"[yolo] Could not load medium model, using nano: {e}")
                self.model = YOLO('yolov8n.pt')
                print("[yolo] ✅ Loaded YOLOv8n (nano)")
            
            self.is_ready = True
            print("[yolo] ⚠️  Note: COCO dataset has limited food classes")
            print("[yolo] Detected foods: banana, apple, orange, broccoli, carrot, sandwich, pizza, hot dog, donut, cake, bottle, cup, bowl, etc.")
            
        except Exception as e:
            print(f"[yolo] ❌ Failed to load YOLOv8: {e}")
            raise

    def detect_and_draw_boxes(self, image_data, topk=25, score_thresh=0.15):
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            results = self.model(image, conf=score_thresh, verbose=False)
            
            detections = []
            all_detections = []
            
            for result in results:
                boxes = result.boxes
                for i, box in enumerate(boxes):
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = result.names[cls]
                    
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    detection = {
                        'label': class_name,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    }
                    all_detections.append(detection)
            
            all_detections.sort(key=lambda x: x['confidence'], reverse=True)
            
            print(f"[yolo] Found {len(all_detections)} total detections above threshold {score_thresh}")
            if len(all_detections) > 0:
                print(f"[yolo] ALL detections (showing top 30):")
                for i, det in enumerate(all_detections[:30]):
                    print(f"  {i+1}. {det['label']}: {det['confidence']:.3f}")
            else:
                print("[yolo] ⚠️  NO detections found! Try lower threshold or different image.")
            
            seen = set()
            unique_detections = []
            for det in all_detections:
                label_lower = det['label'].lower()
                if label_lower not in seen:
                    seen.add(label_lower)
                    unique_detections.append(det)
                    if len(unique_detections) >= topk:
                        break
            
            print(f"[yolo] After deduplication: {len(unique_detections)} unique items")
            
            image_with_boxes = self._draw_boxes(image, unique_detections)
            
            image_data_url = self._image_to_data_url(image_with_boxes)
            
            detections = [
                {
                    'label': det['label'],
                    'confidence': det['confidence']
                }
                for det in unique_detections
            ]
            
            return {
                'detections': detections,
                'image_with_boxes': image_data_url
            }
            
        except Exception as e:
            print(f"[yolo] Error during detection: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _draw_boxes(self, image, detections):
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            font = ImageFont.load_default()
        
        for det in detections:
            bbox = det['bbox']
            label = det['label']
            conf = det['confidence']
            
            draw.rectangle(bbox, outline='#FFD700', width=4)
            
            label_text = f"{label} ({conf:.2f})"
            
            left, top, right, bottom = draw.textbbox((bbox[0], bbox[1]), label_text, font=font)
            text_width = right - left
            text_height = bottom - top
            
            draw.rectangle(
                [bbox[0], bbox[1] - text_height - 4, bbox[0] + text_width + 4, bbox[1]],
                fill='#FFD700'
            )
            
            draw.text((bbox[0] + 2, bbox[1] - text_height - 2), label_text, fill='black', font=font)
        
        return image

    def _image_to_data_url(self, image):
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=90)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"


try:
    yolo_vision_service = YOLOFoodDetector()
except Exception as e:
    print(f"[yolo] Failed to initialize: {e}")
    yolo_vision_service = None
