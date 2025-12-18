import os
from pathlib import Path
from collections import defaultdict

# --- Configuration ---
# Point this to the LABELS folder of your NEW merged dataset
LABEL_ROOT = Path('FinalDataset/train/labels')

# Paste your MASTER_NAMES dictionary here for human-readable output
# Final MASTER_NAMES dictionary containing only the classes that survived the Min 30/Max 300 filter.
# The keys are the names (strings), and the values are the final contiguous indices (0-114).

MASTER_NAMES = {
  'almond': 0,
  'apple': 1,
  'apricot': 2,
  'artichoke': 3,
  'asparagus': 4,
  'avocado': 5,
  'bacon': 6,
  'banana': 7,
  'bean_curd_tofu': 8,
  'beef': 9,
  'beetroot': 10,
  'bell_pepper': 11,
  'black_pepper': 12,
  'blackberry': 13,
  'blueberry': 14,
  'bread': 15,
  'brie_cheese': 16,
  'broccoli': 17,
  'brown_sugar': 18,
  'brussels_sprouts': 19,
  'butter': 20,
  'buttermilk': 21,
  'button_mushroom': 22,
  'cabbage': 23,
  'cantaloupe': 24,
  'carrot': 25,
  'cashew_nut': 26,
  'cauliflower': 27,
  'cayenne_pepper': 28,
  'celery': 29,
  'cheese': 30,
  'cherry': 31,
  'chicken': 32,
  'chicken_stock': 33,
  'chicken_wing': 34,
  'chickpea': 35,
  'chili': 36,
  'cilantro': 37,
  'cinnamon': 38,
  'clementine': 39,
  'coconut': 40,
  'corn': 41,
  'cucumber': 42,
  'date': 43,
  'egg': 44,
  'eggplant': 45,
  'fig': 46,
  'fish': 47,
  'flour': 48,
  'garlic': 49,
  'ginger': 50,
  'gourd': 51,
  'grape': 52,
  'green_bean': 53,
  'green_grape': 54,
  'ham': 55,
  'jalapeno': 56,
  'jam': 57,
  'ketchup': 58,
  'kiwi': 59,
  'ladyfinger': 60,
  'lemon': 61,
  'lettuce': 62,
  'lime': 63,
  'mandarin_orange': 64,
  'mayonnaise': 65,
  'meat': 66,
  'medjool_dates': 67,
  'melon': 68,
  'milk': 69,
  'mozarella_cheese': 70,
  'mushroom': 71,
  'mussel': 72,
  'mustard': 73,
  'noodle': 74,
  'olive_oil': 75,
  'onion': 76,
  'orange': 77,
  'oyster': 78,
  'papaya': 79,
  'paprika': 80,
  'parmesan_cheese': 81,
  'pasta': 82,
  'pea': 83,
  'peach': 84,
  'pear': 85,
  'pickle': 86,
  'pineapple': 87,
  'pork': 88,
  'pork_rib': 89,
  'potato': 90,
  'pumpkin': 91,
  'radish': 92,
  'raspberry': 93,
  'red_beans': 94,
  'red_pepper': 95,
  'rice': 96,
  'salmon': 97,
  'salt': 98,
  'shrimp': 99,
  'spaghetti': 100,
  'spinach': 101,
  'spring_onion': 102,
  'strawberry': 103,
  'sweetcorn': 104,
  'sweet_potato': 105,
  'tomato': 106,
  'tuna': 107,
  'turnip': 108,
  'vegetable_oil': 109,
  'watermelon': 110,
  'white_sugar': 111,
  'yeast': 112,
  'yogurt': 113,
  'zucchini': 114
}
# Reverse the lookup for printing: Index -> Name
MASTER_INDEX_TO_NAME = {index: name for name, index in MASTER_NAMES.items()}
NUM_CLASSES = len(MASTER_NAMES)

# Initialize a dictionary to hold counts: {class_id: count}
class_counts = defaultdict(int)
total_annotations = 0

print(f"--- Starting Annotation Count in: {LABEL_ROOT} ---")

# 1. Iterate through all label files
for label_file in LABEL_ROOT.glob('*.txt'):
    try:
        with open(label_file, 'r') as f:
            for line in f:
                # 2. Extract the Class ID (the first number on the line)
                parts = line.strip().split()
                if not parts:
                    continue
                
                class_id = int(parts[0])
                
                # 3. Tally the count if the ID is within the expected range
                if 0 <= class_id < NUM_CLASSES:
                    class_counts[class_id] += 1
                    total_annotations += 1
                else:
                    # This should not happen with your remapped data, but acts as a check
                    print(f"Warning: Found out-of-range Class ID {class_id} in {label_file.name}")
                    
    except ValueError:
        print(f"Error reading file {label_file.name}. Skipping.")

# 4. Print the Final Report
print("\n--- Final Class Sample Report ---")
print(f"Total Annotations Processed: {total_annotations}\n")

# Sort the results by Master Index for clean viewing
for class_id in sorted(class_counts.keys()):
    count = class_counts[class_id]
    class_name = MASTER_INDEX_TO_NAME.get(class_id, f"UNKNOWN_ID_{class_id}")
    
    # Print in a clean, aligned format
    print(f"ID {class_id: <4} ({class_name: <20}): {count}")

# Check for classes that had zero annotations
for class_id in range(NUM_CLASSES):
    if class_id not in class_counts:
        class_name = MASTER_INDEX_TO_NAME.get(class_id, f"UNKNOWN_ID_{class_id}")
        print(f"ID {class_id: <4} ({class_name: <20}): 0 (MISSING)")