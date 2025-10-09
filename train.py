from ultralytics import YOLO
import os

# --- MODEL CONFIGURATION ---

# Path to the custom dataset YAML file (must be in the project root)
DATA_YAML_PATH = 'oid_ingredients.yaml'

# Path to the pre-trained model weights for transfer learning
MODEL_WEIGHTS = 'yolov8n.pt' 

# Training parameters (Hyperparameters)
TRAINING_ARGS = {
    'data': DATA_YAML_PATH,         # Your custom dataset configuration
    'model': MODEL_WEIGHTS,         # The pre-trained YOLOv8 Nano model
    'epochs': 50,                   # Number of training cycles
    'imgsz': 640,                   # Input image size
    'batch': 8,                     # Batch size (set low for CPU/limited VRAM)
    'name': 'raw_food_ingredients_detector_CPU', # Name for the output runs folder
    'device': 'cpu',                # IMPORTANT: Set to 'cpu' for AMD/CPU-only machines
    'workers': 0,                   # Set to 0 for Windows stability on CPU
    'project': 'runs/detect'        # Base directory for all training runs
}

# --- TRAINING EXECUTION ---

def start_training():
    """Loads the model and starts the training process using defined arguments."""
    print("--- Starting YOLOv8 Training (CPU Mode) ---")
    
    # 1. Load the model (weights file will download if not found)
    model = YOLO(TRAINING_ARGS['model'])

    # 2. Start training
    results = model.train(**TRAINING_ARGS)
    
    # 3. Report completion
    output_dir = os.path.join(TRAINING_ARGS['project'], TRAINING_ARGS['name'])
    print("\n✅ Training complete!")
    print(f"Results and weights saved to: {output_dir}")

if __name__ == '__main__':
    start_training()
