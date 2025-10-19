import collections
from ultralytics import YOLO

# --- SETUP ---
CUSTOM_MODEL_PATH = 'raw_food_ingredients_GPU/raw_food_ingredients_detector_GPU3/weights/best.pt'
model = YOLO(CUSTOM_MODEL_PATH)
video_source = 'ingredients.mp4'  # Assuming your video file is here

# To store all unique instances: {('Apple', 1), ('Cabbage', 2), ('Apple', 5)}
# Note: Use a tuple of (Name, ID) to ensure uniqueness per instance.
unique_instances = set()
total_unique_classes = set()

# ----------------------------------------------------------------------
# 3. Run Tracking (Crucial step for assigning unique IDs)
# ----------------------------------------------------------------------

# We use the track method and specify a tracker. ByteTrack is a good default.
# NOTE: The tracker config files (e.g., 'bytetrack.yaml') are usually found
# in the ultralytics/cfg/trackers folder.
tracking_results = model.track(
    source=video_source, 
    tracker="bytetrack.yaml", 
    persist=True,  # Maintains ID across frames
    save=True,     # Saves the video with tracks
    verbose=False
)

# 4. Process and Extract Unique Track IDs
for r in tracking_results:
    # Check if tracking successfully assigned IDs
    if r.boxes.id is not None:
        # Loop through each detected object's ID and Class ID in the current frame
        for track_id, class_id in zip(r.boxes.id.tolist(), r.boxes.cls.tolist()):
            name = r.names[int(class_id)]
            
            # Store the unique tuple (Class Name, Track ID)
            unique_instances.add((name, int(track_id)))
            
            # Store the unique class name for final tally
            total_unique_classes.add(name)


# 5. Final Tally: Count Unique Items by Class Name
# This extracts the name part from the unique_instances set
all_unique_names = [name for name, _ in unique_instances]

# Use Counter on the list of unique names (one entry per tracked object)
item_counts = collections.Counter(all_unique_names)

# Format and sort the final output
final_output = [f"{count} {item}" for item, count in item_counts.items()]
final_output_sorted = sorted(final_output)


print("--- Unique Ingredient Count (Video Tracking) ---")
print(f"Video Source: {video_source}")
print(f"Total Unique Objects Tracked (Across All Classes): {len(unique_instances)}") 
print(f"Total Unique Classes Present: {len(total_unique_classes)}") 
print("Unique Detected Items with Counts:", final_output_sorted)
print("------------------------------------------------")