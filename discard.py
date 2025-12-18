import os
import shutil
import random
from pathlib import Path
from tqdm import tqdm
import sys

# ====================================================================
# 1. CONFIGURATION AND THRESHOLDS
# ====================================================================

# --- THRESHOLDS ---
MIN_SAMPLES = 30  # Classes below this count will be removed.
MAX_SAMPLES = 300 # Classes above this count will be randomly sampled down.
# ------------------

# --- PATHS ---
# Source directory is the output of your previous merge run
SOURCE_ROOT = Path('./merged_final_data_full') 
# Destination directory for the new, balanced dataset
DEST_ROOT = Path('./merged_final_data_balanced')

SPLITS = ['train', 'val', 'test']

# MASTER_NAMES (Full list of 140 classes for mapping)
# NOTE: This list must be EXACTLY the same as in your previous merge script
MASTER_NAMES = {
    # Fruit, Nut, and Grains (0-29)
    'almond': 0, 'apple': 1, 'apricot': 2, 'artichoke': 3, 'asparagus': 4,
    'avocado': 5, 'bacon': 6, 'banana': 7, 'bean': 8, 'bean_curd_tofu': 9,
    'bean_sprout': 10, 'beef': 11, 'beetroot': 12, 'bell_pepper': 13,
    'black_pepper': 14, 'blackberry': 15, 'blueberry': 16, 'bok_choy': 17,
    'bread': 18, 'brie_cheese': 19, 'broccoli': 20, 'brown_sugar': 21,
    'brussels_sprouts': 22, 'butter': 23, 'buttermilk': 24, 'button_mushroom': 25,
    'cabbage': 26, 'cantaloupe': 27, 'carrot': 28, 'cashew_nut': 29,
    
    # Vegetables and Herbs (30-59)
    'cauliflower': 30, 'cayenne_pepper': 31, 'celery': 32, 'cheddar_cheese': 33,
    'cheese': 34, 'cherry': 35, 'chicken': 36, 'chicken_breast': 37,
    'chicken_stock': 38, 'chicken_wing': 39, 'chickpea': 40, 'chili': 41,
    'chocolate': 42, 'cilantro': 43, 'cinnamon': 44, 'clementine': 45,
    'coconut': 46, 'corn': 47, 'cucumber': 48, 'date': 49,
    'dry_grape': 50, 'durian': 51, 'egg': 52, 'eggplant': 53,
    'fig': 54, 'fish': 55, 'flour': 56, 'garlic': 57,
    'ginger': 58, 'gourd': 59,
    
    # Fruits, Meats, and Dairy (60-89)
    'grape': 60, 'green_bean': 61, 'green_grape': 62, 'ham': 63,
    'guava': 64,  'jalapeno': 65, 'jam': 66, 'ketchup': 67, 'kiwi': 68,
    'ladyfinger': 69, 'lemon': 70, 'lettuce': 71, 'lime': 72, 'lobster': 73,
    'mandarin_orange': 74, 'mango': 75, 'mangosteen': 76, 'mayonnaise': 77,
    'meat': 78, 'meat_ball': 79, 'medjool_dates': 80, 'melon': 81, 'milk': 82,
    'mozarella_cheese': 83, 'mushroom': 84, 'mussel': 85, 'mustard': 86,
    'noodle': 87, 'oil': 88, 'olive_oil': 89, 
    
    # Produce and Staples (90-139)
    'onion': 90, 'orange': 91, 'oyster': 92, 'papaya': 93, 'paprika': 94,
    'parmesan_cheese': 95, 'pasta': 96, 'pea': 97, 'peach': 98, 'pear': 99,
    'persimmon': 100, 'pickle': 101, 'pineapple': 102, 'pomegranate': 103,
    'pork': 104, 'pork_belly': 105, 'pork_rib': 106, 'potato': 107,
    'prune': 108, 'pumpkin': 109, 'radish': 110, 'raspberry': 111,
    'red_beans': 112, 'red_pepper': 113, 'rice': 114, 'rice_vinegar': 115,
    'salad': 116, 'salmon': 117, 'salt': 118, 'scallop': 119, 'shrimp': 120,
    'soy_sauce': 121, 'spaghetti': 122, 'spinach': 123, 'spring_onion': 124,
    'starfruit': 125, 'stilton_cheese': 126, 'strawberry': 127, 'sweetcorn': 128,
    'sweet_potato': 129, 'tomato': 130, 'tuna': 131, 'turnip': 132,
    'vegetable': 133, 'vegetable_oil': 134, 'watermelon': 135, 'white_sugar': 136,
    'yeast': 137, 'yogurt': 138, 'zucchini': 139 
}

# Reverse mapping: Index -> Name
MASTER_ID_TO_NAME = {index: name for name, index in MASTER_NAMES.items()}


# --- SAMPLE COUNTS (Copied directly from your last output) ---
# NOTE: This dictionary maps the MASTER_ID (0-139) to the total number of annotations.
# We will use this to determine which images to keep.
SAMPLE_COUNTS = {
    0: 1797, 1: 11531, 2: 50, 3: 122, 4: 909, 5: 1225, 6: 93, 7: 35001, 8: 15, 9: 139, 10: 3, 11: 369, 12: 409, 13: 4539, 14: 246, 15: 189, 16: 2049, 17: 9, 18: 570, 19: 75, 20: 8434, 21: 189, 22: 329, 23: 723, 24: 213, 25: 297, 26: 580, 27: 147, 28: 12589, 29: 300, 30: 917, 31: 34, 32: 751, 33: 3, 34: 300, 35: 612, 36: 360, 37: 0, 38: 348, 39: 45, 40: 174, 41: 1528, 42: 12, 43: 246, 44: 210, 45: 101, 46: 219, 47: 1942, 48: 1881, 49: 46, 50: 12, 51: 21, 52: 3020, 53: 1180, 54: 144, 55: 133, 56: 285, 57: 1461, 58: 445, 59: 57, 60: 5057, 61: 1674, 62: 45, 63: 336, 64: 9, 65: 479, 66: 60, 67: 297, 68: 522, 69: 603, 70: 2116, 71: 4059, 72: 1036, 73: 6, 74: 213, 75: 21, 76: 6, 77: 336, 78: 360, 79: 12, 80: 309, 81: 123, 82: 804, 83: 66, 84: 4261, 85: 327, 86: 309, 87: 81, 88: 18, 89: 63, 90: 8275, 91: 8745, 92: 546, 93: 73, 94: 54, 95: 102, 96: 453, 97: 1874, 98: 586, 99: 627, 100: 22, 101: 422, 102: 1315, 103: 3, 104: 30, 105: 0, 106: 45, 107: 6840, 108: 8, 109: 282, 110: 965, 111: 445, 112: 276, 113: 270, 114: 483, 115: 9, 116: 6, 117: 369, 118: 225, 119: 15, 120: 286, 121: 6, 122: 81, 123: 468, 124: 1525, 125: 0, 126: 9, 127: 2904, 128: 436, 129: 549, 130: 10035, 131: 108, 132: 643, 133: 9, 134: 303, 135: 578, 136: 309, 137: 408, 138: 66, 139: 566
}

# ====================================================================
# 2. FILE OPERATION LOGIC (Balancing)
# ====================================================================

def balance_dataset():
    print(f"--- Starting Dataset Balancing (Min: {MIN_SAMPLES}, Max: {MAX_SAMPLES}) ---")
    
    # 1. Filter Classes based on Min Threshold and Find Image Stems
    images_to_keep_by_class = {}  # {master_id: [list of unique image stems]}
    kept_master_indices = set()
    
    for master_id, total_count in SAMPLE_COUNTS.items():
        master_name = MASTER_ID_TO_NAME[master_id]
        
        # Check 1: Minimum Threshold
        if total_count < MIN_SAMPLES:
            print(f"[DISCARDED] ID {master_id: <4} ({master_name: <20}): Below MIN ({total_count} < {MIN_SAMPLES})")
            continue
            
        # Class is kept; find all image stems containing this class
        image_stems_for_class = []
        for split in SPLITS:
            labels_dir = SOURCE_ROOT / split / 'labels'
            if not labels_dir.exists(): continue
            
            for label_file in labels_dir.glob('*.txt'):
                try:
                    with open(label_file, 'r') as f:
                        if any(line.startswith(f"{master_id} ") for line in f):
                            # The file stem is the unique image identifier (e.g., dataset1_imgX)
                            image_stems_for_class.append(label_file.stem)
                except Exception as e:
                    print(f"Error reading {label_file}: {e}")
                    
        
        # 2. Apply Maximum Sampling (Down-sampling)
        unique_stems = list(set(image_stems_for_class))
        
        if len(unique_stems) > MAX_SAMPLES:
            random.seed(42) # Ensure deterministic sampling
            unique_stems = random.sample(unique_stems, MAX_SAMPLES)
            print(f"[SAMPLED] ID {master_id: <4} ({master_name: <20}): Reduced from {total_count} to {len(unique_stems)} images.")
        else:
            print(f"[KEPT]    ID {master_id: <4} ({master_name: <20}): {len(unique_stems)} images.")
            
        images_to_keep_by_class[master_id] = unique_stems
        kept_master_indices.add(master_id)


    # 3. Aggregate Final Image List and Annotations
    final_image_stems = {} # {stem: original_split}
    final_annotations = {} # {stem: set_of_new_lines}
    
    # Create output directories
    for split in SPLITS:
        (DEST_ROOT / split / 'images').mkdir(parents=True, exist_ok=True)
        (DEST_ROOT / split / 'labels').mkdir(parents=True, exist_ok=True)

    
    # Create the mapping for the NEW contiguous indices
    sorted_kept_indices = sorted(list(kept_master_indices))
    old_to_new_index_map = {old_id: new_id for new_id, old_id in enumerate(sorted_kept_indices)}
    
    
    # 4. Process and Rewrite Labels
    total_images_processed = 0
    
    # PHASE 2: Rewrite files based on the sampling decision
    for split in SPLITS:
        source_labels_dir = SOURCE_ROOT / split / 'labels'
        source_images_dir = SOURCE_ROOT / split / 'images'
        
        for stem in tqdm(os.listdir(source_labels_dir), desc=f"Rewriting {split} split"):
            stem = Path(stem).stem
            
            # Check if this image stem belongs to ANY class that survived the filter
            is_kept = False
            for master_id in images_to_keep_by_class.keys():
                if stem in images_to_keep_by_class[master_id]:
                    is_kept = True
                    break

            if is_kept:
                # Read the original label file
                original_label_path = source_labels_dir / f"{stem}.txt"
                new_annotations = set()
                
                with open(original_label_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 5: continue
                        
                        old_master_id = int(parts[0])
                        
                        # Only keep annotations for classes that survived the MIN filter
                        if old_master_id in old_to_new_index_map:
                            new_class_id = old_to_new_index_map[old_master_id]
                            annotation_data = ' '.join(parts[1:])
                            new_annotations.add(f"{new_class_id} {annotation_data}")
                            
                
                # --- Copy and Write ---
                
                # Copy the image (assuming .jpg for simplicity, generalize if necessary)
                original_image_path_jpg = source_images_dir / f"{stem}.jpg"
                original_image_path_png = source_images_dir / f"{stem}.png"
                
                source_path = original_image_path_jpg if original_image_path_jpg.exists() else original_image_path_png

                if source_path.exists():
                    shutil.copy(source_path, DEST_ROOT / split / 'images' / source_path.name)
                    
                    # Write the new label file
                    dest_label_path = DEST_ROOT / split / 'labels' / f"{stem}.txt"
                    with open(dest_label_path, 'w') as f:
                        f.writelines(line + '\n' for line in sorted(list(new_annotations)))
                    
                    total_images_processed += 1
                    
    # 5. Create Final YAML
    final_nc = len(sorted_kept_indices)
    final_names_list = {new_id: MASTER_ID_TO_NAME[old_id] for old_id, new_id in old_to_new_index_map.items()}

    yaml_content = f"""
# Final data.yaml for Ingredient Object Detection Training
# Generated after balancing (nc: {final_nc}, Min: {MIN_SAMPLES}, Max: {MAX_SAMPLES}).

train: {DEST_ROOT.name}/train/images
val: {DEST_ROOT.name}/val/images
test: {DEST_ROOT.name}/test/images

nc: {final_nc}

names:
"""
    for index in sorted(final_names_list.keys()):
        yaml_content += f"  {index}: {final_names_list[index]}\n"

    yaml_path = DEST_ROOT / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
        
    print(f"\n✅ Balancing Complete! Total images in new dataset: {total_images_processed}")
    print(f"   New dataset located at: {DEST_ROOT.name} (Classes Kept: {final_nc})")

if __name__ == "__main__":
    balance_dataset()