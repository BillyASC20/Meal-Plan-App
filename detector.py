import collections
from ultralytics import YOLO

# --- MODEL PATH CHANGE ---
# 1. Load the Custom Trained Model
CUSTOM_MODEL_PATH = 'runs/detect/raw_food_ingredients_detector_CPU/weights/best.pt'
model = YOLO(CUSTOM_MODEL_PATH)
# -------------------------

# 2. Define the Input Source
image_source = 'ingredients3.jpg'

# 3. Run Prediction (Inference)
# Pass save=False to disable saving the image to the 'runs/' folder.
# We also set verbose=False to minimize command line clutter.
results = model.predict(source=image_source, save=False, verbose=False)

# 4. Process and Extract UNIQUE Names
#detected_names = set() # Use a set to automatically store only unique names

# Store ALL detected names in this list (including duplicates)
all_detections = [] 

for r in results:
    # r.boxes.cls contains the class ID (e.g., 42) for every detected object
    # r.names is a dictionary mapping the ID to the name (e.g., 42: 'bottle')

    # Iterate through all detected class IDs in the image
    for class_id in r.boxes.cls:
        # Get the name using the ID and add it to the set
        name = r.names[int(class_id)]
        all_detections.append(name)

# 5. Output Final List
# Convert the set to a list for a final, clean output
#final_list = sorted(list(detected_names))

# 5. Tally and Output Final Count
# Use Counter to count the occurrences of each name
item_counts = collections.Counter(all_detections)

# Format the output as a list of strings: ["3 Apple", "1 Broccoli", "2 Tomato"]
final_output = [f"{count} {item}" for item, count in item_counts.items()]
final_output_sorted = sorted(final_output)

# print("--- Prediction Results ---")
# print(f"Image Source: {image_source}")
# print(f"Total Unique Objects Detected: {len(final_list)}")
# print("List of Unique Detected Items:", final_list)
# print("--------------------------")

print("--- Prediction Results ---")
print(f"Image Source: {image_source}")
# The total count is simply the length of the list of ALL detections
print(f"Total Objects Detected: {len(all_detections)}") 
print(f"Total Unique Classes Detected: {len(item_counts)}") 
print("List of Detected Items with Counts:", final_output_sorted)
print("--------------------------")