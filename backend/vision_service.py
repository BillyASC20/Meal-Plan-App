import base64
import io
import os
from PIL import Image
from ultralytics import YOLO
import cv2
import numpy as np
import torch

# Fix PyTorch 2.6 weights_only security issue for YOLO models
try:
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
except (AttributeError, ImportError):
    # Older PyTorch version or unable to import
    pass

class VisionService:
    def __init__(self):
        """
        Initialize YOLOv8 model.
        
        Options:
        1. Use pre-trained model (yolov8n.pt) - detects common objects
        2. Use custom trained model - put your trained weights in backend/models/
        """
        # Check for custom trained model first
        custom_model = 'models/ingredients.pt'
        if os.path.exists(custom_model):
            print(f"🎯 Loading custom trained model: {custom_model}")
            self.model = YOLO(custom_model)
        else:
            # Pre-trained model is TRASH for ingredients - only detects generic objects
            # This is just a placeholder until you train your own model
            model_path = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
            print(f"⚠️  WARNING: Using generic pre-trained model (NOT optimized for food)")
            print(f"    This will detect containers/objects, not ingredients!")
            print(f"    Train your own model for real ingredient detection!")
            print(f"    See TRAINING_GUIDE.md")
            self.model = YOLO(model_path)
        
        # Common food items that YOLO can detect
        # You'll expand this when you train your own model
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
            'knife': None,  # Ignore utensils
            'fork': None,
            'spoon': None,
        }
    
    def detect_ingredients(self, base64_image):
        """
        Detect ingredients from base64 encoded image.
        
        Args:
            base64_image: Base64 encoded image string (with or without data URL prefix)
        
        Returns:
            List of detected ingredient names
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            # Decode base64 to image
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL Image to numpy array for YOLO
            img_array = np.array(image)
            
            # Run YOLO inference
            results = self.model(img_array, conf=0.25)  # 25% confidence threshold
            
            # Extract detected classes
            detected_ingredients = set()
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class name
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    print(f"Detected: {class_name} (confidence: {confidence:.2f})")
                    
                    # Map to food ingredient if applicable
                    if class_name in self.food_mappings:
                        mapped_name = self.food_mappings[class_name]
                        if mapped_name:  # Not None (ignore utensils)
                            detected_ingredients.add(mapped_name)
            
            # Convert to list and return
            ingredients = list(detected_ingredients)
            
            if not ingredients:
                print("⚠️  No FOOD items detected. Using fallback ingredients.")
                print("💡 TIP: Try uploading photos with: apple, banana, orange, broccoli, carrot, pizza, etc.")
                # Fallback to common ingredients if nothing detected
                ingredients = ["chicken", "rice", "vegetables"]
            
            print(f"✅ Final detected ingredients: {ingredients}")
            return ingredients
            
        except Exception as e:
            print(f"Error detecting ingredients: {str(e)}")
            # Fallback on error
            return ["chicken", "rice", "vegetables"]
    
    def train_custom_model(self, dataset_path, epochs=50):
        """
        Train a custom YOLOv8 model on your ingredient images.
        
        Steps to prepare your training data:
        1. Collect images of ingredients you want to detect
        2. Label them using Roboflow or LabelImg (free tools)
        3. Export in YOLOv8 format
        4. Put in backend/datasets/ingredients/
        
        Dataset structure:
        datasets/ingredients/
            ├── data.yaml
            ├── train/
            │   ├── images/
            │   └── labels/
            └── val/
                ├── images/
                └── labels/
        
        Args:
            dataset_path: Path to your prepared dataset
            epochs: Number of training epochs (50 is good starting point)
        """
        print(f"Training custom model on {dataset_path}...")
        
        # Train on your custom dataset
        results = self.model.train(
            data=dataset_path,
            epochs=epochs,
            imgsz=640,
            batch=16,
            name='ingredient_detector',
            patience=10,  # Early stopping
            save=True,
            device='cpu'  # Use 'cuda' if you have GPU
        )
        
        print("Training complete! Model saved to runs/detect/ingredient_detector/weights/best.pt")
        print("Copy the best.pt file to backend/models/ingredients.pt to use it")
        
        return results

# Create singleton instance
vision_service = VisionService()
