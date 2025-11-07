# Hugging Face Spaces Deployment Guide

## Why Hugging Face Spaces?

- ✅ **FREE forever** (not a trial)
- ✅ **16GB RAM** (handles YOLOv8 easily)
- ✅ **No sleep mode** (always available)
- ✅ **Built for ML** (they expect large models)
- ✅ **Auto-deploy from GitHub**
- ✅ **Free GPU option** if you need it later

## Quick Setup (5 minutes)

### Step 1: Create Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Name: `meal-plan-detector`
4. SDK: Choose **Gradio** or **Streamlit** (we'll use Gradio)
5. Click "Create Space"

### Step 2: Add Files

Create these files in your Space:

**app.py** (main file):
```python
import gradio as gr
from ultralytics import YOLO
from PIL import Image
import numpy as np

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

def detect_ingredients(image):
    """Detect ingredients from uploaded image."""
    # Run YOLO detection
    results = model(image, conf=0.25)
    
    # Extract detected items
    detected = []
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls]
            detected.append(f"{name} ({conf:.2f})")
    
    return detected if detected else ["No food items detected"]

# Create Gradio interface
demo = gr.Interface(
    fn=detect_ingredients,
    inputs=gr.Image(type="pil"),
    outputs=gr.Textbox(label="Detected Ingredients"),
    title="🍳 Meal Plan Ingredient Detector",
    description="Upload a photo of food to detect ingredients"
)

if __name__ == "__main__":
    demo.launch()
```

**requirements.txt**:
```
ultralytics
pillow
gradio
```

### Step 3: That's It!

Hugging Face auto-builds and deploys. You get a URL like:
`https://huggingface.co/spaces/YOUR_USERNAME/meal-plan-detector`

---

## Connect to Your React Frontend

Your frontend can call the Hugging Face Space API:

```typescript
// frontend/src/pages/CameraPage.tsx

const detectIngredients = async () => {
  const response = await fetch(
    'https://YOUR_USERNAME-meal-plan-detector.hf.space/api/predict',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: [uploadedImage]
      })
    }
  )
  
  const result = await response.json()
  setDetectedItems(result.data[0])
}
```

---

## Alternative: Keep Your Current Backend

If you want to keep your Flask backend structure:

**Use Hugging Face Spaces with Custom Docker:**

Create `Dockerfile` in backend:
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860"]
```

Push to Hugging Face Space with Docker SDK.

---

## Cost Comparison

| Platform | Monthly Cost | RAM | Sleep Mode |
|----------|-------------|-----|------------|
| **Hugging Face** | **$0** | 16GB | Never |
| Railway | $5-7 | 1GB | After 15min |
| Render | $0-7 | 512MB | After 15min |
| Google Cloud Run | $0.50-2 | Pay per use | Auto-scales |
| Vercel + HF | $0 | Unlimited | Never |

---

## 🎯 Best Setup for Your Senior Project

**Frontend:** Vercel (free)  
**ML Backend:** Hugging Face Spaces (free)  
**Recipe Generation:** Keep OpenAI API call in frontend directly  

**Total Cost: $0 + OpenAI usage only**

---

## Want Me to Convert Your App?

I can convert your current Flask backend to work with Hugging Face Spaces in like 10 minutes. Want me to do it?
