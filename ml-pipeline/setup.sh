#!/bin/bash

echo "=========================================="
echo "ML Pipeline Setup"
echo "=========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Place your CSV files in the data/ directory:"
echo "   - ingredient_6L.csv"
echo "   - unique_indexed_ingredients.csv"  
echo "   - cleaned_ingredients.csv"
echo ""
echo "2. Train the model:"
echo "   python train_classifier.py"
echo ""
echo "3. Test predictions:"
echo "   python predict.py --ingredients 'cheese,butter,cream'"
echo ""
