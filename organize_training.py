"""
Organize training artifacts after YOLOv8 training completes
Moves training results to archive and deploys best model
"""
import shutil
import os
from pathlib import Path

if __name__ == '__main__':
    print("=" * 60)
    print("🗂️  Organizing Training Artifacts")
    print("=" * 60)
    
    # Paths
    project_root = Path(__file__).parent
    runs_dir = project_root / "runs" / "detect" / "food101"
    training_archive = project_root / "training_archive"
    weights_dir = runs_dir / "weights"
    best_model = weights_dir / "best.pt"
    deploy_model = project_root / "backend" / "models" / "ingredients.pt"
    
    # Check if training completed
    if not best_model.exists():
        print("❌ Training not complete! best.pt not found.")
        print(f"   Looking for: {best_model}")
        exit(1)
    
    print(f"✅ Found trained model: {best_model}")
    print(f"   Size: {best_model.stat().st_size / (1024*1024):.2f} MB")
    
    # Create training archive directory
    training_archive.mkdir(exist_ok=True)
    archive_dest = training_archive / "food101_training"
    
    # Move training results to archive
    if archive_dest.exists():
        print(f"⚠️  Archive already exists, removing old version...")
        shutil.rmtree(archive_dest)
    
    print(f"\n📦 Moving training artifacts to archive...")
    shutil.move(str(runs_dir), str(archive_dest))
    print(f"   ✅ Moved: runs/detect/food101 → training_archive/food101_training")
    
    # Copy best model to deployment location
    print(f"\n🚀 Deploying model to backend...")
    
    # Backup old model if exists
    if deploy_model.exists():
        backup = deploy_model.parent / "ingredients_old.pt"
        shutil.copy(str(deploy_model), str(backup))
        print(f"   📋 Backed up old model to: {backup.name}")
    
    # Copy new model
    shutil.copy(str(archive_dest / "weights" / "best.pt"), str(deploy_model))
    print(f"   ✅ Deployed: best.pt → backend/models/ingredients.pt")
    print(f"   Size: {deploy_model.stat().st_size / (1024*1024):.2f} MB")
    
    # Create README for training archive
    readme_content = """# Training Archive: Food-101 Model

## Training Details

**Model:** YOLOv8n (nano)  
**Dataset:** Food-101 Subset (25,250 images, 101 classes)  
**Training Images:** 20,200  
**Validation Images:** 5,050  
**Epochs:** 100 (with early stopping, patience=15)  
**Batch Size:** 16  
**Image Size:** 640x640  
**Device:** CUDA (RTX 3070)

## Directory Contents

- `weights/` - Trained model weights
  - `best.pt` - Best model (highest validation accuracy)
  - `last.pt` - Last epoch model
- `results.csv` - Training metrics per epoch
- `confusion_matrix.png` - Confusion matrix visualization
- `results.png` - Training/validation curves
- `args.yaml` - Training configuration

## Classes (101 Food Types)

apple_pie, baby_back_ribs, baklava, beef_carpaccio, beef_tartare, beet_salad, 
beignets, bibimbap, bread_pudding, breakfast_burrito, bruschetta, caesar_salad, 
cannoli, caprese_salad, carrot_cake, ceviche, cheese_plate, cheesecake, 
chicken_curry, chicken_quesadilla, chicken_wings, chocolate_cake, chocolate_mousse, 
churros, clam_chowder, club_sandwich, crab_cakes, creme_brulee, croque_madame, 
cup_cakes, deviled_eggs, donuts, dumplings, edamame, eggs_benedict, escargots, 
falafel, filet_mignon, fish_and_chips, foie_gras, french_fries, french_onion_soup, 
french_toast, fried_calamari, fried_rice, frozen_yogurt, garlic_bread, gnocchi, 
greek_salad, grilled_cheese_sandwich, grilled_salmon, guacamole, gyoza, hamburger, 
hot_and_sour_soup, hot_dog, huevos_rancheros, hummus, ice_cream, lasagna, 
lobster_bisque, lobster_roll_sandwich, macaroni_and_cheese, macarons, miso_soup, 
mussels, nachos, omelette, onion_rings, oysters, pad_thai, paella, pancakes, 
panna_cotta, peking_duck, pho, pizza, pork_chop, poutine, prime_rib, 
pulled_pork_sandwich, ramen, ravioli, red_velvet_cake, risotto, samosa, sashimi, 
scallops, seaweed_salad, shrimp_and_grits, spaghetti_bolognese, spaghetti_carbonara, 
spring_rolls, steak, strawberry_shortcake, sushi, tacos, takoyaki, tiramisu, 
tuna_tartare, waffles

## Model Deployment

The best model has been automatically deployed to:
```
backend/models/ingredients.pt
```

## Reproducing Training

To retrain this model:
```bash
python train_model.py
```

Original dataset: Food-101 from HuggingFace (ethz/food101)
Dataset preparation: `download_dataset.py`

---
*Training completed: """ + str(Path(archive_dest / "weights" / "best.pt").stat().st_mtime) + "*"
    
    readme_path = archive_dest / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"\n📄 Created README: {readme_path.relative_to(project_root)}")
    
    print("\n" + "=" * 60)
    print("✅ Organization Complete!")
    print("=" * 60)
    print(f"📁 Training artifacts: training_archive/food101_training/")
    print(f"🚀 Deployed model: backend/models/ingredients.pt")
    print(f"🎯 Ready to use! Restart backend to load new 101-class model.")
    print("=" * 60)
