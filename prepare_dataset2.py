import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import settings
import os

# --- CONFIGURATION ---
# The classes list is now based on the wider OID Classification set (Existence Check).
# Note: The classes below are a mix of raw ingredients and common prepared foods/staples.
TARGET_CLASSES = [
    # --- Produce / Raw Ingredients (25) ---
    "Apple", "Artichoke", "Banana", "Bell pepper", "Broccoli", 
    "Cabbage", "Cantaloupe", "Carrot", "Coconut", "Cucumber", 
    "Common fig", "Grape", "Grapefruit", "Lemon", "Mango", 
    "Mushroom", "Orange", "Peach", "Pear", "Pineapple", 
    "Pomegranate", "Potato", "Pumpkin", "Radish", "Tomato",
    "Zucchini", "Garden Asparagus",
    
    # --- Staples / Dairy / Baked Goods (15) ---
    "Bagel", "Baked goods", "Bread", "Cake", 
    "Cheese", "Cookie", "Cream", "Croissant", "Dairy Product", 
    "Dessert", "Doughnut", "Egg (Food)", "Ice cream", "Milk", 
    "Pancake", "Pasta", "Pastry", "Pretzel",
    
    # --- Prepared Food / Seafood (15) ---
    "Burrito", "Chicken", "Crab", "Fast food", "Fish", 
    "French fries", "Hamburger", "Hot dog", "Oyster", "Pizza", 
    "Salad", "Sandwich", "Seafood", "Shrimp", "Snack", 
    "Squid", "Sushi", "Taco", "Tart", "Turkey",
    
    # --- Drinks / Condiments (5) ---
    "Beer", "Cocktail", "Coffee", "Drink", "Juice",
    "Tea", "Wine"
]

# IMPORTANT: Increase MAX_SAMPLES significantly (e.g., 5000) for good training results!
MAX_SAMPLES = 5000 
DATASET_NAME = "oid-raw-ingredients-cls" # Changed dataset name for classification

# Set the directory where FiftyOne will store the raw dataset
DATASET_ROOT = os.path.join(settings.get("datasets_dir"), DATASET_NAME)

# --- 1. Download and Filter the Open Images Dataset (CLASSIFICATION MODE) ---
print(f"Starting download and filtering for {len(TARGET_CLASSES)} classes...")
dataset = foz.load_zoo_dataset(
    "open-images-v7", 
    split="train", 
    # CRITICAL CHANGE 1: Use classifications for faster training and wider class coverage
    label_types=["classifications"], 
    classes=TARGET_CLASSES, 
    max_samples=MAX_SAMPLES,
    dataset_name=DATASET_NAME,
    # CRITICAL CHANGE 2: Specify the classification field name
    label_field="positive_labels" 
)

# --- 2. Export the Filtered Dataset to YOLO CLASSIFICATION Format ---
# The target export format is now ImageClassificationDirectoryTree, 
# which creates folders named after each class.
EXPORT_DIR = os.path.join(os.getcwd(), "OID_YOLO_CLS_DATA")
print(f"Exporting data to YOLO CLASSIFICATION format in: {EXPORT_DIR}")

dataset.export(
    export_dir=EXPORT_DIR,
    # CRITICAL CHANGE 3: Use the format for classification directory trees
    dataset_type=fo.types.ImageClassificationDirectoryTree 
    # The classification export automatically uses the directory structure for labeling.
)
print("\n--- Dataset Preparation Complete ---")
print(f"Data is ready for training in the '{EXPORT_DIR}' folder.")

# --- 3. Save the class names and paths for the YAML file (CLASSIFICATION) ---
# Create the YAML file that Ultralytics YOLOv8 Classification expects.
yaml_content = f"""
# Ultralytics YOLOv8 Dataset YAML for Food Classification

# Dataset Root
path: {EXPORT_DIR}

# Train/Val data (folders inside EXPORT_DIR)
train: train
val: val

# Number of classes
nc: {len(TARGET_CLASSES)}

# Class Names
# The names array must match the folder names created by the exporter.
names: {TARGET_CLASSES}
"""
# Use a NEW YAML file name for the classification task
yaml_filepath = os.path.join(os.getcwd(), "oid_ingredients_cls.yaml")
with open(yaml_filepath, "w") as f:
    f.write(yaml_content)

print(f"A classification configuration file ({yaml_filepath}) has been created.")
print("\nNEXT STEP: Update your train.py to use 'yolov8n-cls.pt' and this new YAML file.")
