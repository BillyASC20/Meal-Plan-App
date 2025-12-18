import os
from pathlib import Path
import random
# --- Configuration ---
# Point this to the LABELS folder of your NEW merged dataset
FINAL_LABEL_DIR = Path('./foodseg103_low_samples_only/train/labels')

# Classes to check (select a few easy ones and the problematic ones)
CLASSES_TO_CHECK = [
    (2, 'apricot'),
    (4, 'asparagus'),
    (26, 'cashew_nut'),
    (29, 'celery'),
    (31, 'cherry'),
    (43, 'date'),
    (102, 'spring_onion'),
]
random.seed(42)
print("--- Starting Final Label Verification ---")

for class_id, class_name in CLASSES_TO_CHECK:
    found_images = []
    
    # Iterate through all label files in the merged dataset
    for label_file in FINAL_LABEL_DIR.glob('*.txt'):
        with open(label_file, 'r') as f:
            for line in f:
                # Check if the line starts with the target class ID
                if line.startswith(f"{class_id} "):
                    # The image name stem is the label file name without '.txt'
                    image_stem = label_file.stem 
                    
                    # The unique stem includes the original dataset name (e.g., dataset1_0001)
                    # The script prints this unique stem for easy tracking
                    found_images.append(image_stem)
                    break # Move to next label file
        
        # Stop check after finding a reasonable sample size
        if len(found_images) >= 5:
            break

    print(f"\n✅ Class {class_id} ({class_name}): Found {len(found_images)} samples.")
    if found_images:
        print(f"   Sample File Stem(s): {', '.join(found_images)}")

print("\n--- Verification Complete ---")