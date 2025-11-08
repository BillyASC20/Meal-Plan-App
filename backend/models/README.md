# Model Deployment

## Quick Setup

1. **Place your trained model here:**
   ```
   backend/models/ingredients.pt
   ```

2. **The model will be automatically loaded** when the backend starts.

## Testing Locally

```powershell
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The server will load your `ingredients.pt` model automatically.

## Deployment Checklist

✅ Place your `.pt` file in this directory as `ingredients.pt`
✅ File should be ~6-20 MB (YOLOv11-nano)
✅ Trained on food/ingredient images
✅ Backend will load it automatically on startup

## API Endpoint

```
POST /detect-ingredients
Body: { "image": "base64_encoded_image" }
Response: { "ingredients": ["apple", "banana", ...] }
```

## File Structure

```
backend/
  models/
    ingredients.pt  ← Your trained model (YOU NEED TO ADD THIS)
  app.py            ← Flask server (auto-loads the model)
  vision_service.py ← Handles YOLO inference
```

## Troubleshooting

**Model not loading?**
- Check file name is exactly `ingredients.pt`
- Check file size (should be MB, not KB)
- Check logs when starting app.py

**Wrong detections?**
- Model might be trained on wrong classes
- Try lowering confidence threshold in vision_service.py (line 82)

**Deployment platforms:**
- HuggingFace Spaces (recommended)
- Railway
- Render
- Heroku
