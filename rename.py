import os
import shutil
from pathlib import Path
from tqdm import tqdm
import sys 

# ====================================================================
# 1. MASTER CLASS CONFIGURATION (CRITICALLY FIXED NAMES)
# ====================================================================

# MASTER_NAMES (Master Name to Index - nc: 140)
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

# DATASET_CONFIGS (CRITICALLY FIXED)
DATASET_CONFIGS = {
    'dataset1': {
        0: 'almond', 1: 'apple', 2: 'asparagus', 3: 'avocado', 4: 'bacon', 5: 'banana', 6: 'bean', 7: 'bean_sprout', 8: 'beef', 9: 'beetroot', 10: 'bell_pepper', 11: 'blackberry', 12: 'blueberry', 13: 'bok_choy', 14: 'bread', 15: 'brie_cheese', 16: 'broccoli', 17: 'cabbage', 18: 'carrot', 19: 'cauliflower', 20: 'cheddar_cheese', 21: 'cheese', 22: 'cherry', 23: 'chicken_breast', 24: 'chicken_wing', 25: 'chili', 
        26: 'chocolate', 27: 'corn', 28: 'cucumber', 29: 'dry_grape', 30: 'durian', 31: 'egg', 32: 'eggplant', 33: 'fish', 34: 'garlic', 35: 'ginger', 36: 'grape', 37: 'green_grape', 38: 'bell_pepper', # Fixed 'green pepper'
        39: 'guava', 40: 'jalapeno', 41: 'jam', 42: 'kiwi', 43: 'lemon', 44: 'mango', 45: 'mangosteen', # Fixed 'mangoteen'
        46: 'meat_ball', 47: 'milk', 48: 'mozarella_cheese', 49: 'mushroom', 50: 'mussel', 51: 'noodle', 52: 'onion', 53: 'orange', 54: 'oyster', 55: 'papaya', 56: 'parmesan_cheese', 57: 'pasta', 58: 'pineapple', 59: 'pomegranate', 60: 'pork', 61: 'pork_belly', 62: 'pork_rib', 63: 'potato', 64: 'pumpkin', 65: 'raspberry', 66: 'salad', 67: 'salmon', 68: 'scallop', 69: 'shrimp', 70: 'spring_onion', 71: 'starfruit', 72: 'stilton_cheese', 73: 'strawberry', 74: 'sweet_potato', 75: 'tomato', 76: 'tuna', 77: 'vegetable', 78: 'watermelon', 79: 'yogurt'
    },
    'dataset2': {
        0: 'almond', 1: 'apple', 2: 'apricot', 3: 'artichoke', 4: 'asparagus', 5: 'avocado', 6: 'banana', 7: 'bean_curd_tofu', # Fixed 'bean curd/tofu'
        8: 'bell_pepper', # Fixed 'bell pepper/capsicum'
        9: 'blackberry', 10: 'blueberry', 11: 'broccoli', 12: 'brussels_sprouts', 13: 'cantaloupe', # Fixed 'cantaloup/cantaloupe'
        14: 'carrot', 15: 'cauliflower', 16: 'cayenne_pepper', # Fixed cayenne/cayenne spice/pepper/red pepper
        17: 'celery', 18: 'cherry', 19: 'chickpea', # Fixed 'chickpea/garbanzo'
        20: 'chili', # Fixed chili/chili vegetable/pepper/chilli/chilly
        21: 'clementine', 22: 'coconut', # Fixed 'coconut/cocoanut'
        23: 'corn', # Fixed edible corn/corn/maize
        24: 'cucumber', # Fixed 'cucumber/cuke'
        25: 'date', # Fixed 'date/date fruit'
        26: 'eggplant', # Fixed 'eggplant/aubergine'
        27: 'fig', # Fixed 'fig/fig fruit'
        28: 'garlic', # Fixed 'garlic/ail'
        29: 'ginger', # Fixed 'ginger/gingerroot'
        30: 'strawberry', 31: 'gourd', 32: 'grape', 33: 'green_bean', 34: 'spring_onion', # Fixed 'green onion/spring onion/scallion'
        35: 'tomato', 36: 'kiwi', # Fixed 'kiwi fruit'
        37: 'lemon', 38: 'lettuce', 39: 'lime', 40: 'mandarin_orange', 41: 'melon', 42: 'mushroom', 43: 'onion', 44: 'orange', # Fixed 'orange/orange fruit'
        45: 'papaya', 46: 'pea', # Fixed 'pea/pea food'
        47: 'peach', 48: 'pear', 49: 'persimmon', 50: 'pickle', 51: 'pineapple', 52: 'potato', 53: 'prune', 54: 'pumpkin', 55: 'radish', # Fixed 'radish/daikon'
        56: 'raspberry', 57: 'strawberry', 58: 'sweet_potato', 59: 'tomato', 60: 'turnip', 61: 'watermelon', 62: 'zucchini' # Fixed 'zucchini/courgette'
    },
    'dataset3': {
        0: 'banana', 1: 'potato', 2: 'apple', 3: 'avocado', 4: 'broccoli', 5: 'cabbage', 6: 'carrot', 7: 'chicken', 8: 'corn', 9: 'cucumber', 10: 'egg', 11: 'eggplant', 12: 'fish', 13: 'garlic', 14: 'mushroom', 15: 'onion', 16: 'orange', 17: 'pineapple', 18: 'shrimp', 19: 'tomato'
    },
    'dataset4': {
        0: 'apple', 1: 'asparagus', 2: 'avocado', 3: 'bacon', 4: 'banana', 5: 'bean', # Fixed 'beans'
        6: 'beef', 7: 'bell_pepper', # Fixed 'bell peppers'
        8: 'black_pepper', 9: 'blueberry', 10: 'bread', 11: 'broccoli', 12: 'butter', 13: 'cabbage', 14: 'carrot', 15: 'cauliflower', 16: 'celery', 17: 'button_mushroom', # Fixed 'champignons'
        18: 'cheese', 19: 'chicken', 20: 'chili', 21: 'corn', 22: 'cucumber', 23: 'egg', 24: 'eggplant', 25: 'egg', # Duplicates 'egg'
        26: 'garlic', 27: 'ginger', 28: 'ham', 29: 'ketchup', 30: 'lemon', 31: 'lettuce', 32: 'lime', 33: 'lobster', 34: 'meat', 35: 'milk', 36: 'mussel', 37: 'oil', 38: 'olive_oil', 39: 'onion', 40: 'paprika', 41: 'pickle', # Fixed 'pickles'
        42: 'potato', 43: 'rice', 44: 'rice_vinegar', 45: 'salt', 46: 'soy_sauce', 47: 'spaghetti', 48: 'spinach', 49: 'spring_onion', 50: 'strawberry', 51: 'pork', # Fixed 'susages' (assuming it should be pork)
        52: 'tomato'
    },
    'dataset5': {
        0: 'beetroot', 1: 'bell_pepper', # Fixed 'bellpepper'
        2: 'cabbage', 3: 'carrot', 4: 'cauliflower', 5: 'chili', # Fixed 'chillipepper'
        6: 'corn', 7: 'cucumber', 8: 'eggplant', 9: 'garlic', 10: 'ginger', 11: 'jalapeno', 12: 'ladyfinger', 13: 'lemon', 14: 'lettuce', 15: 'onion', 16: 'pea', # Fixed 'peas'
        17: 'potato', 18: 'radish', 19: 'spinach', 20: 'sweetcorn', 21: 'sweet_potato', # Fixed 'sweetpotato'
        22: 'tomato', 23: 'turnip'
    },
    'dataset6': {
        0: 'apple', 1: 'rice', # Fixed 'Basmatirice'
        2: 'black_pepper', # Fixed 'Blackpepper'
        3: 'broccoli', 4: 'brown_sugar', # Fixed 'Brownsugar'
        5: 'butter', 6: 'buttermilk', 7: 'button_mushroom', # Fixed 'Buttonmushroom'
        8: 'cashew_nut', # Fixed 'Cashewnut'
        9: 'chicken_stock', # Fixed 'Chickenstock'
        10: 'cilantro', 11: 'cinnamon', 12: 'egg', 13: 'flour', 14: 'garlic', 15: 'bell_pepper', # Fixed 'Greenpepper'
        16: 'lemon', 17: 'mayonnaise', 18: 'medjool_dates', # Fixed 'Medjooldates'
        19: 'mustard', 20: 'onion', 21: 'pea', # Fixed 'Peas'
        22: 'potato', 23: 'red_beans', # Fixed 'Redbeans'
        24: 'red_pepper', # Fixed 'Redpepper'
        25: 'salt', 26: 'spring_onion', # Fixed 'Springonion'
        27: 'tomato', 28: 'vegetable_oil', # Fixed 'Vegetableoil'
        29: 'white_sugar', # Fixed 'Whitesugar'
        30: 'milk', 31: 'yeast'
    }
}

# ====================================================================
# 2. FILE OPERATION LOGIC (FINAL CLEAN MERGE SCRIPT)
# ====================================================================

# --- Configuration ---
SOURCE_ROOT = Path('.') 
DEST_ROOT = Path('./merged_final_data_full') # Using 'full' name to reflect no sampling
DATASET_NAMES = list(DATASET_CONFIGS.keys())
SPLITS = ['train', 'val', 'test']

def generate_remap_dict(ds_name):
    """Generates the final lookup: Old Index -> New Master Index."""
    old_class_map = DATASET_CONFIGS[ds_name]
    remap_dict = {}
    for old_index, master_name in old_class_map.items():
        if master_name in MASTER_NAMES:
            remap_dict[old_index] = MASTER_NAMES[master_name]
        else:
            print(f"FATAL ERROR: Master name '{master_name}' not found for {ds_name}. Script aborted.", file=sys.stderr)
            sys.exit(1)
    return remap_dict

# FINAL CLEAN FUNCTION (REPLACES ALL OLD MERGE/COUNT FUNCTIONS)
def merge_and_remap_full():
    """Performs merging and remapping, keeping ALL samples (no discarding/sampling)."""
    
    # 1. INITIAL SETUP
    print("Starting Merging and Full Remapping...")
    
    # Structure: {master_index: {image_name: set_of_annotations}, ...}
    all_annotations_by_class = {i: {} for i in range(len(MASTER_NAMES))}
    
    # Dictionary to track which images belong to which split
    image_to_split_map = {}
    
    # Set to store the unique image stems that are processed (for final copying)
    unique_image_stems_to_copy = set()
    
    # Create destination directories
    for split in SPLITS:
        (DEST_ROOT / split / 'images').mkdir(parents=True, exist_ok=True)
        (DEST_ROOT / split / 'labels').mkdir(parents=True, exist_ok=True)

    # 2. ITERATE AND REMAP (The Core Logic)
    for ds_name in tqdm(DATASET_NAMES, desc="PHASE 1: Remapping and Staging"):
        remap_dict = generate_remap_dict(ds_name)
        
        for split in SPLITS:
            source_labels_dir = SOURCE_ROOT / ds_name / split / 'labels'
            source_images_dir = SOURCE_ROOT / ds_name / split / 'images'
            
            if not source_labels_dir.exists():
                continue

            for label_file in source_labels_dir.glob('*.txt'):
                
                # Check for image file existence (.jpg and .png)
                image_file_jpg = source_images_dir / label_file.name.replace('.txt', '.jpg')
                image_file_png = source_images_dir / label_file.name.replace('.txt', '.png')
                
                source_image_path = None
                if image_file_jpg.exists():
                    source_image_path = image_file_jpg
                elif image_file_png.exists():
                    source_image_path = image_file_png
                else:
                    continue # Skip if no image found

                unique_name_stem = f"{ds_name}_{label_file.stem}" 
                image_to_split_map[unique_name_stem] = split 
                unique_image_stems_to_copy.add(unique_name_stem) # KEEP ALL IMAGES

                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5: continue
                    
                    old_index = int(parts[0])
                    
                    if old_index in remap_dict:
                        new_index = remap_dict[old_index]
                        annotation_data = ' '.join(parts[1:])
                        full_new_line = f"{new_index} {annotation_data}"
                        
                        if new_index not in all_annotations_by_class:
                             all_annotations_by_class[new_index] = {}

                        if unique_name_stem not in all_annotations_by_class[new_index]:
                            all_annotations_by_class[new_index][unique_name_stem] = set()
                        
                        all_annotations_by_class[new_index][unique_name_stem].add(full_new_line)

    # 3. FINAL COPYING AND LABEL WRITING
    print("\nPHASE 2: Copying Images and Writing Final Labels")
    final_files_copied = 0
    
    for unique_name_stem in tqdm(list(unique_image_stems_to_copy), desc="Copying Files"):
        original_split = image_to_split_map[unique_name_stem]
        ds_name = unique_name_stem.split('_')[0]
        original_file_stem = unique_name_stem.split('_', 1)[1]
        
        # --- Find Original Image Path (already checked in Phase 1, just get path) ---
        source_images_dir = SOURCE_ROOT / ds_name / original_split / 'images'
        
        source_image_path = None
        for ext in ['.jpg', '.png']: 
            temp_path = source_images_dir / f"{original_file_stem}{ext}"
            if temp_path.exists():
                source_image_path = temp_path
                break
        
        if source_image_path is None:
            continue

        # 3a. Aggregate all annotations for this image
        final_annotations = set()
        for class_index in all_annotations_by_class:
            if unique_name_stem in all_annotations_by_class[class_index]:
                final_annotations.update(all_annotations_by_class[class_index][unique_name_stem])

        # 3b. Write the new label file
        dest_label_path = DEST_ROOT / original_split / 'labels' / f"{unique_name_stem}.txt"
        with open(dest_label_path, 'w') as f:
            sorted_annotations = sorted(list(final_annotations), key=lambda x: int(x.split(' ')[0]))
            f.writelines(line + '\n' for line in sorted_annotations)

        # 3c. Copy the image file
        image_extension = source_image_path.suffix 
        dest_image_path = DEST_ROOT / original_split / 'images' / f"{unique_name_stem}{image_extension}"
        shutil.copy(source_image_path, dest_image_path)
        
        final_files_copied += 1

    # 4. Final YAML Generation
    create_final_yaml_full(DEST_ROOT, MASTER_NAMES)

    print(f"\n✅ Merging and Full Remapping complete! Total unique images copied: {final_files_copied}")
    print(f"The merged dataset (ALL samples kept) is in the '{DEST_ROOT}' folder.")


def create_final_yaml_full(dest_root, master_names):
    """
    Creates the final data.yaml file with ALL 140 MASTER_NAMES.
    """
    
    # 1. Create the Final Training Names list from the Master Dictionary
    final_names = {}
    master_name_lookup = {index: name for name, index in master_names.items()}
    
    for index in sorted(master_name_lookup.keys()):
        final_names[index] = master_name_lookup[index]

    final_nc = len(final_names)
    
    # 2. Write the YAML content
    yaml_content = f"""
# Final data.yaml for Ingredient Object Detection Training
# Generated after merging and full remapping (140 total classes).

train: {dest_root.name}/train/images
val: {dest_root.name}/val/images
test: {dest_root.name}/test/images

nc: {final_nc}

names:
"""
    for index, name in final_names.items():
        yaml_content += f"  {index}: {name}\n"

    # 3. Save the YAML file
    yaml_path = dest_root / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
        
    print(f"✅ Final YAML created successfully: {yaml_path.name} (nc: {final_nc})")


if __name__ == "__main__":
    # The call MUST be merge_and_remap_full()
    merge_and_remap_full()