import fiftyone as fo
import fiftyone.zoo as foz
from ultralytics import settings
import os

# --- CONFIGURATION ---
# ⚠️ IMPORTANT: Replace this with YOUR comprehensive list of raw ingredients!
# TARGET_CLASSES = [
#     "Apple", "Banana", "Broccoli", "Carrot", "Tomato", 
#     "Orange", "Potato", "Cucumber", "Bell pepper", "Cheese", "Chicken"
# ] 

#updated classes that are taken directly from zoolist1.py output.
#there are 601 
TARGET_CLASSES = [
    # --- Produce / Raw Ingredients (25) ---
    "Apple", "Artichoke", "Banana", "Bell pepper", "Broccoli", 
    "Cabbage", "Cantaloupe", "Carrot", "Coconut", "Cucumber", 
    "Common fig", "Grape", "Grapefruit", "Lemon", "Mango", 
    "Mushroom", "Orange", "Peach", "Pear", "Pineapple", 
    "Pomegranate", "Potato", "Pumpkin", "Radish", "Tomato",
    "Zucchini", "Garden Asparagus",
    
    # --- Staples / Dairy / Baked Goods (15) ---
    "Bagel", "Baked goods", "Bread", "Butter", "Cake", 
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
MAX_SAMPLES = 500  # Adjust: Start with 500-1000 for a quick test; increase for better results
DATASET_NAME = "oid-raw-ingredients"

# Set the directory where FiftyOne will store the raw dataset
DATASET_ROOT = os.path.join(settings.get("datasets_dir"), DATASET_NAME)


# 1. Download and Filter the Open Images Dataset
print(f"Starting download and filtering for {len(TARGET_CLASSES)} classes...")
dataset = foz.load_zoo_dataset(
    "open-images-v7", 
    split="train", 
    label_types=["detections"], # Tells FiftyOne to download detection annotations
    classes=TARGET_CLASSES, 
    max_samples=MAX_SAMPLES,
    dataset_name=DATASET_NAME,
    # CRITICAL: Specify the field name where the detections should be stored!
    # By default, for OID, this is typically 'detections' if you use the argument.
    label_field="detections"
)

# 2. Export the Filtered Dataset to YOLO Format
# This will now correctly find the "detections" field that was created in step 1.
EXPORT_DIR = os.path.join(os.getcwd(), "OID_YOLO_DATA")
print(f"Exporting data to YOLO format in: {EXPORT_DIR}")

dataset.export(
    export_dir=EXPORT_DIR,
    dataset_type=fo.types.YOLOv5Dataset,  
    label_field="detections", 
    classes=TARGET_CLASSES
)
print("\n--- Dataset Preparation Complete ---")
print(f"Data is ready for training in the '{EXPORT_DIR}' folder.")

# 3. Save the class names and paths for the YAML file
# Create a simplified YAML for Ultralytics
yaml_content = f"""
# Ultralytics YOLOv8 Dataset YAML for Raw Ingredients

# Dataset Root
path: {EXPORT_DIR}

# Train/Val/Test data (assuming FiftyOne exported a single 'train' split)
train: images
val: images

# Number of classes
nc: {len(TARGET_CLASSES)}

# Class Names
names: {TARGET_CLASSES}
"""

with open(os.path.join(os.getcwd(), "oid_ingredients.yaml"), "w") as f:
    f.write(yaml_content)

print(f"A configuration file (oid_ingredients.yaml) has been created in your root folder.")