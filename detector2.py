from ultralytics import YOLO
import os

# --- MODEL PATH CHANGE ---
# 1. Load the Custom Trained Classification Model
# IMPORTANT: Use the path from your classification training run!
CUSTOM_MODEL_PATH = 'runs/classify/food_classification_V1/weights/best.pt'
model = YOLO(CUSTOM_MODEL_PATH)
# -------------------------

# 2. Define the Input Source
image_source = 'ingredients3.jpg'
# CHANGE 1: Define a larger number of predictions to show
TOP_K = 15 

# 3. Run Prediction (Inference)
results = model.predict(source=image_source, save=False, verbose=False)

# 4. Process and Extract Classification Results
all_results = []

for r in results:
    if r.probs is None:
        all_results.append((f"No Classification Data Found for {r.path}", 0.0))
        continue
    
    # --- NEW LOGIC: Extract Top K predictions ---
    # We retrieve the Top 15 predictions using r.probs.topk(k=TOP_K) 
    # This gives us the indices (IDs) and values (Confidences) of the top K scores.
    top_k_tuple = r.probs.topk(k=TOP_K) 
    top_k_ids = top_k_tuple.indices 
    top_k_confidences = top_k_tuple.values
    
    image_results = []
    
    for i in range(TOP_K):
        # We need .item() to convert the PyTorch tensors to basic Python types
        class_id = top_k_ids[i].item()
        confidence = top_k_confidences[i].item() * 100 # Convert to percentage
        predicted_name = r.names[class_id]
        
        # Only include predictions over a reasonable threshold (e.g., 10%)
        # This filters out random, low-confidence guesses.
        if confidence > 10.0:
            image_results.append((predicted_name, confidence))

    all_results.append(image_results)

# 5. Output Final List
print("--- Classification Prediction Results (Top K Extended) ---")
print(f"Image Source: {image_source}")
print(f"Model Used: {CUSTOM_MODEL_PATH}")

if all_results and all_results[0]:
    print(f"\nTop {TOP_K} Predictions (Confidence > 10.0%):")
    # Sort by confidence descending
    for name, conf in sorted(all_results[0], key=lambda x: x[1], reverse=True):
        print(f"- {name}: {conf:.2f}%")
else:
    print("No confident predictions found.")
print("--------------------------")
