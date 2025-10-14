from ultralytics import YOLO
import os

# --- MODEL CONFIGURATION ---

# CHANGE 1: Point to the new classification YAML file created by prepare_dataset.py
DATA_YAML_PATH = 'oid_ingredients_cls.yaml'

# CHANGE 2: Use the classification-specific model weights
MODEL_WEIGHTS = 'yolov8n-cls.pt' 

# Training parameters (Hyperparameters)
TRAINING_ARGS = {
    'data': DATA_YAML_PATH,         # Your custom dataset configuration
    'model': MODEL_WEIGHTS,         # The pre-trained YOLOv8 Classification model
    'epochs': 50,                   # Number of training cycles
    'imgsz': 224,                   # OPTIMIZATION: Standard input size for classification models
    'batch': 64,                    # OPTIMIZATION: Increased batch size for faster CPU training
    'name': 'food_classification_V1', # CHANGE 3: New, unique run name for classification
    'device': 'cpu',                # Keep on 'cpu' unless your AMD/ROCm setup is verified working
    'workers': 0,                   # Keep at 0 for Windows stability
    'project': 'runs/classify'      # CHANGE 4: Use a folder dedicated to classification runs
}

# --- TRAINING EXECUTION ---

def start_training():
    """Loads the model and starts the training process using defined arguments."""
    print("--- Starting YOLOv8 Image Classification Training (Existence Check) ---")
    
    # 1. Load the model (weights file 'yolov8n-cls.pt' will download if not found)
    model = YOLO(TRAINING_ARGS['model'])

    # 2. Start training
    # NOTE: YOLO will automatically infer the task is 'classify' due to the model file used.
    results = model.train(**TRAINING_ARGS)
    
    # 3. Report completion
    output_dir = os.path.join(TRAINING_ARGS['project'], TRAINING_ARGS['name'])
    print("\n✅ Training complete!")
    print(f"Results and weights saved to: {output_dir}")

if __name__ == '__main__':
    start_training()
