# Food-101 Dataset (Subset: ~25k images)

## Dataset Info
- **Images**: ~25,000 (subset sampled from full dataset)
- **Classes**: 101 prepared food dishes
- **Sampling**: ~250 images per class (balanced)
- **Size**: ~3-4 GB
- **Training Time**: 5-7 hours on RTX 3070
- **Source**: https://huggingface.co/datasets/ethz/food101

## Classes Included (101 Food Types)

### 🍕 Italian:
- Pizza
- Spaghetti Bolognese
- Spaghetti Carbonara
- Lasagna
- Ravioli
- Gnocchi
- Risotto
- Bruschetta
- Caprese Salad
- Cannoli
- Tiramisu
- Panna Cotta

### 🍔 American:
- Hamburger
- Hot Dog
- French Fries
- Onion Rings
- Mac and Cheese
- Grilled Cheese Sandwich
- Club Sandwich
- Pulled Pork Sandwich
- Lobster Roll Sandwich
- Nachos
- Chicken Wings
- Donuts
- Pancakes
- Waffles
- French Toast
- Cheesecake
- Carrot Cake
- Red Velvet Cake
- Chocolate Cake
- Cupcakes
- Brownies
- Ice Cream
- Frozen Yogurt

### � Asian:
- Sushi
- Sashimi
- Ramen
- Pho
- Pad Thai
- Spring Rolls
- Gyoza
- Dumplings
- Edamame
- Bibimbap
- Takoyaki
- Miso Soup
- Hot and Sour Soup
- Fried Rice
- Peking Duck

### � International:
- Paella (Spanish)
- Tacos (Mexican)
- Huevos Rancheros (Mexican)
- Guacamole (Mexican)
- Falafel (Middle Eastern)
- Hummus (Middle Eastern)
- Baklava (Middle Eastern)
- Escargots (French)
- Foie Gras (French)
- French Onion Soup
- Croque Madame (French)
- Creme Brulee (French)
- Macarons (French)
- Beignets (French)
- Bread Pudding
- Samosa (Indian)
- Chicken Curry (Indian)

### 🥩 Proteins:
- Steak
- Filet Mignon
- Prime Rib
- Pork Chop
- Baby Back Ribs
- Beef Carpaccio
- Beef Tartare
- Grilled Salmon
- Fish and Chips
- Fried Calamari
- Shrimp and Grits
- Oysters
- Mussels
- Scallops
- Crab Cakes
- Lobster Bisque
- Clam Chowder
- Tuna Tartare
- Ceviche
- Chicken Quesadilla

### 🥗 Salads & Healthy:
- Caesar Salad
- Greek Salad
- Caprese Salad
- Beet Salad
- Seaweed Salad

### � Breakfast:
- Eggs Benedict
- Omelette
- Deviled Eggs
- Breakfast Burrito

### 🍰 Desserts:
- Apple Pie
- Strawberry Shortcake
- Chocolate Mousse
- Churros
- Poutine (Canadian)

### 🍞 Sides:
- Garlic Bread
- Cheese Plate

## Quick Start

### 1. Install Dependencies
```bash
pip install datasets pillow pyyaml tqdm
```

### 2. Download Dataset (Subset)
```bash
python download_dataset.py
```

This will:
- Download Food-101 from HuggingFace
- Sample ~250 images per class (total ~25k images)
- Create balanced train/validation split
- Convert to YOLO format
- Save to `datasets/food101-subset/`

### 3. Manual Configuration

You can adjust the sampling in `download_dataset.py`:
```python
IMAGES_PER_CLASS = 250  # Change this for more/less images per class
TRAIN_SPLIT = 0.8       # 80% train, 20% validation
```

## Dataset Structure

After download:
```
datasets/food101-subset/
├── data.yaml
├── train/
│   ├── images/
│   │   ├── 000000.jpg
│   │   ├── 000001.jpg
│   │   └── ...
│   └── labels/
│       ├── 000000.txt
│       ├── 000001.txt
│       └── ...
└── valid/
    ├── images/
    └── labels/
```

## Training

Train with:
```bash
python train_model.py
```

## Expected Results

- **Accuracy**: 85-90% mAP@0.5 (with 25k images)
- **Model Size**: 8-12 MB
- **Inference Speed**: 30-50 FPS on RTX 3070
- **Training Epochs**: 100 (recommended)
- **Training Time**: 5-7 hours on RTX 3070

## Why This Dataset?

✅ **101 diverse food classes** - Industry standard benchmark
✅ **Balanced sampling** - Equal representation across all classes
✅ **Manageable size** - 25k images trains in reasonable time
✅ **High quality** - Professional food photography
✅ **From HuggingFace** - No API key needed, free to use
✅ **Prepared dishes** - Perfect for meal recognition/planning
✅ **Covers all cuisines** - Italian, American, Asian, Middle Eastern, French, Indian, etc.

## Notes

⚠️ **First download** may take 10-20 minutes (downloads full dataset then samples)  
💡 **Subsequent runs** will be faster (HuggingFace caches the dataset)  
📦 **Full dataset** is 5GB, subset is ~3-4GB

