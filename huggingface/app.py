import gradio as gr
from ultralytics import YOLO
from PIL import Image
import os

# Load YOLOv8 model
# Will use pre-trained first, you can replace with your trained model later
model_path = 'models/ingredients.pt' if os.path.exists('models/ingredients.pt') else 'yolov8n.pt'
print(f"Loading model: {model_path}")
model = YOLO(model_path)

# Food item mappings (expand this based on your training)
food_mappings = {
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
}

def detect_ingredients(image):
    """
    Detect food ingredients from an uploaded image.
    
    Args:
        image: PIL Image from Gradio
    
    Returns:
        str: Comma-separated list of detected ingredients
    """
    if image is None:
        return "Please upload an image"
    
    try:
        # Run YOLO detection
        results = model(image, conf=0.25)
        
        # Extract detected food items
        detected_ingredients = set()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class name
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0])
                
                print(f"Detected: {class_name} (confidence: {confidence:.2f})")
                
                # Map to food ingredient if applicable
                if class_name in food_mappings:
                    mapped_name = food_mappings[class_name]
                    if mapped_name:
                        detected_ingredients.add(mapped_name)
        
        # Return results
        if detected_ingredients:
            ingredients_list = sorted(list(detected_ingredients))
            return ", ".join(ingredients_list)
        else:
            return "No food items detected. Try uploading a photo with visible food items like fruits, vegetables, or prepared dishes."
    
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=detect_ingredients,
    inputs=gr.Image(type="pil", label="Upload Food Photo"),
    outputs=gr.Textbox(label="Detected Ingredients", placeholder="Ingredients will appear here..."),
    title="🍳 Meal Plan - Ingredient Detector",
    description="""
    Upload a photo of your ingredients or food items, and AI will detect what's in the image!
    
    **Currently detects:** Fruits, vegetables, prepared foods, and common ingredients.
    
    **Tips for best results:**
    - Good lighting
    - Clear view of ingredients
    - One or multiple items visible
    """,
    examples=[
        # You can add example images here later
    ],
    theme=gr.themes.Soft(),
    allow_flagging="never"
)

if __name__ == "__main__":
    demo.launch()
