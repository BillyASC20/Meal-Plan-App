import fiftyone.zoo as foz

# Load a minimal number of samples (just 1) to retrieve the dataset structure
print("Loading Open Images V7 metadata to retrieve the full class list...")
dataset = foz.load_zoo_dataset(
    "open-images-v7", 
    split="train", 
    label_types=["detections"], # Focus on classes with detection boxes
    max_samples=1,              # Only need the metadata, not the data
    dataset_name="oid-class-list-temp"
)

# The default_classes property contains the full list of names supported by OID
all_detection_classes = dataset.default_classes

print(f"\nTotal OID Detection Classes Found: {len(all_detection_classes)}")
# Print the entire list (or save it to a file)
print(all_detection_classes) 

# Delete the temporary dataset object to keep your environment clean
dataset.delete()