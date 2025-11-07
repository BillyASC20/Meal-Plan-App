# 🚀 Quick Deployment Guide - NO BS Edition

You have thousands of food images and need this deployed. Here's the simplest path:

## Option 1: Train Locally → Deploy to HF (What You're Asking)

**Yes, you can train locally then deploy.** Here's how:

### Step 1: Train Your Model Locally (This Takes Time)

Your dataset is already prepared at `backend/datasets/food41-yolo/`:
- 225 food classes
- 93,988 training images
- 23,588 validation images

**Run training** (this will take 1-3 hours on your Mac):
```bash
cd backend
python train_model.py
```

This uses:
- Your Apple M2 GPU (MPS) automatically
- Default: 50 epochs, 320px images, batch size 16
- Output: `runs/detect/food_detector/weights/best.pt`

**What happens while training:**
- Epoch 1/50 → learning basic patterns
- Epoch 10/50 → getting better at detecting fruits
- Epoch 30/50 → fine-tuning detection accuracy
- Epoch 50/50 → final model saved

Progress updates every epoch. Just let it run.

### Step 2: Copy Trained Model to HF Folder

After training finishes:
```bash
cd backend
mkdir -p ../huggingface/models
cp runs/detect/food_detector/weights/best.pt ../huggingface/models/ingredients.pt
```

### Step 3: Deploy to Hugging Face Spaces (FREE Forever)

1. **Create Space:**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `meal-plan-detector`
   - SDK: **Gradio**
   - Hardware: **CPU basic (free)**
   - Visibility: **Public**
   - Click "Create Space"

2. **Upload Files:**
   - Click "Files" tab in your new Space
   - Upload these 3 files:
     - `huggingface/app.py`
     - `huggingface/requirements.txt`
     - `huggingface/models/ingredients.pt` (your trained model)

3. **Wait for Build:**
   - HF will auto-install dependencies (~3-5 minutes)
   - Status will change from "Building" → "Running"
   - You'll get a URL like: `https://YOUR_USERNAME-meal-plan-detector.hf.space`

### Step 4: Test Your Deployed Model

Open your Space URL in browser:
- Upload a food image
- Should detect ingredients and show them

Test the API endpoint:
```bash
# Replace with your actual Space URL
curl -X POST "https://YOUR_USERNAME-meal-plan-detector.hf.space/api/predict" \
  -H "Content-Type: application/json" \
  -d '{"data":[{"data":"data:image/jpeg;base64,/9j/4AAQ...","name":"test.jpg"}]}'
```

### Step 5: Connect Your Frontend

Update `frontend/src/pages/CameraPage.tsx`:
```typescript
// Replace this line:
const API_URL = 'http://localhost:5001/detect-ingredients';

// With your HF Space URL:
const API_URL = 'https://YOUR_USERNAME-meal-plan-detector.hf.space/api/predict';
```

Then adjust the API call format (see HUGGINGFACE_DEPLOY.md for details).

---

## Option 2: Use Pre-trained Model First (Deploy NOW, Train Later)

Don't want to wait 1-3 hours? Deploy with the basic pre-trained model:

### Quick Deploy (5 minutes):

1. **Copy pre-trained model:**
```bash
cd backend
mkdir -p ../huggingface/models
cp yolov8n.pt ../huggingface/models/ingredients.pt
```

2. **Upload to HF Space** (same as Step 3 above)
   - `huggingface/app.py`
   - `huggingface/requirements.txt`
   - `huggingface/models/ingredients.pt` (pre-trained)

3. **Your app works NOW** (but detects generic objects, not specific ingredients)

4. **Train custom model later**, then replace `models/ingredients.pt` in your Space

---

## Option 3: Train in Google Colab (FASTEST - 15-20 mins with FREE GPU)

See `COLAB_TRAINING.md` for full guide.

**TL;DR:**
1. Upload your dataset to Google Drive
2. Open Colab, mount Drive
3. Run training cells (free T4 GPU = way faster)
4. Download `best.pt`
5. Upload to HF Space

---

## What I Recommend

**For RIGHT NOW:**
1. Start local training in background (it'll take a while but requires zero setup)
2. Meanwhile, deploy with pre-trained model so your frontend works
3. When training finishes, replace the model file in your Space

**Commands to run RIGHT NOW:**
```bash
# Terminal 1: Start training (background it)
cd /Users/zc/Desktop/Meal-Plan-App/backend
nohup python train_model.py > training.log 2>&1 &

# Terminal 2: Deploy pre-trained model to HF
cd /Users/zc/Desktop/Meal-Plan-App/backend
mkdir -p ../huggingface/models
cp yolov8n.pt ../huggingface/models/ingredients.pt

# Now upload huggingface/ folder to HF Space
```

Check training progress:
```bash
tail -f /Users/zc/Desktop/Meal-Plan-App/backend/training.log
```

---

## Cost Breakdown

- Local training: **$0** (uses your Mac)
- Google Colab GPU: **$0** (free tier)
- Hugging Face Spaces: **$0** (free tier, 16GB RAM, no sleep)
- Vercel frontend: **$0** (free tier)
- OpenAI API (recipes): **~$0.01-0.05 per generation** (pay per use)

**Total deployment cost: $0/month** ✅

---

## Need Help?

- Training stuck? Check `backend/training.log` or press Ctrl+C and restart
- HF Space failing? Check the "Logs" tab in your Space dashboard
- Frontend not connecting? Make sure you updated the API URL in CameraPage.tsx
- Model not detecting well? Pre-trained is generic; custom training needed

## Files You Need

Already in your repo:
- ✅ `huggingface/app.py` - Gradio interface
- ✅ `huggingface/requirements.txt` - Dependencies
- ✅ `backend/datasets/food41-yolo/` - Your prepared dataset
- ✅ `backend/train_model.py` - Training script

After training:
- ⏳ `runs/detect/food_detector/weights/best.pt` - Your trained model
- ⏳ Copy to: `huggingface/models/ingredients.pt` - For deployment
