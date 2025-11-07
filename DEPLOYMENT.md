# 🚀 Deployment Guide - Meal Plan App

## Quick Deploy (FREE)

### Frontend → Vercel (5 mins)

1. **Push to GitHub** (if not already)
   ```bash
   cd /Users/zc/Desktop/Meal-Plan-App
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **Deploy to Vercel**
   - Go to https://vercel.com
   - Sign in with GitHub
   - Click "New Project"
   - Import `Meal-Plan-App` repo
   - Select `frontend` folder as root directory
   - Click "Deploy"
   - Done! Get your URL: `https://meal-plan-app-xxx.vercel.app`

---

### Backend → Render (10 mins)

1. **Go to Render**
   - Visit https://render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub → Select `Meal-Plan-App` repo
   - Name: `meal-plan-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **Add Environment Variables**
   - Click "Environment" tab
   - Add: `OPENAI_API_KEY` = `your_key_here`
   - Add: `PORT` = `10000` (Render default)
   - Add: `HOST` = `0.0.0.0`

4. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes (installing PyTorch is slow)
   - Get your backend URL: `https://meal-plan-backend.onrender.com`

---

### Connect Frontend to Backend

1. **Update Frontend API URL**
   - In your Vercel dashboard
   - Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://meal-plan-backend.onrender.com`
   - Redeploy

2. **Or edit code directly:**
   ```typescript
   // frontend/src/pages/CameraPage.tsx
   const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
   
   fetch(`${API_URL}/detect-ingredients`, {
     // ...
   })
   ```

---

## ⚠️ Free Tier Limitations

**Render Free:**
- ❌ Spins down after 15 mins of inactivity
- ❌ Cold start = 30-60 seconds
- ❌ Limited to 512MB RAM (might be tight for YOLOv8)
- ✅ Good enough for demos/presentations

**Solution for Presentation Day:**
- Upgrade to Render $7/month for 1 month
- Or use Railway $5/month
- Cancel after you present

---

## 🚂 Alternative: Railway (Recommended for ML)

**Better for your app because:**
- Faster cold starts
- More RAM (1GB free tier)
- Better for ML models
- Easier setup

**Deploy to Railway:**
```bash
# Install CLI
brew install railway

# Login
railway login

# Deploy
cd /Users/zc/Desktop/Meal-Plan-App
railway init
railway up

# Add environment variables
railway variables set OPENAI_API_KEY=your_key_here
```

Done! Railway gives you URLs for both frontend and backend.

---

## 📱 Share Your App

**After deployment:**
1. Frontend: `https://meal-plan-app.vercel.app`
2. Backend: `https://meal-plan-backend.onrender.com`
3. Share frontend URL with anyone!
4. They can upload photos and get recipes!

---

## 🎓 For Your Senior Project Presentation

**Before Demo Day:**
1. Test everything on deployed version
2. Have backup screenshots/video in case it's slow
3. Consider upgrading to paid tier ($5-7) for 1 month
4. Monitor usage in dashboard
5. Have localhost version as backup

**Cost for 1 month presentation:**
- Vercel: FREE
- Render: $7/month or Railway: $5/month
- Total: ~$5-7 for professional deployment

Worth it for a senior project! Cancel after you present.

---

## 🔥 Pro Tips

1. **Use smaller model for free tier:**
   - YOLOv8n (nano) instead of YOLOv8m
   - Faster and uses less RAM

2. **Keep backend warm:**
   - Use a free uptime monitor (UptimeRobot)
   - Pings your backend every 5 minutes
   - Prevents cold starts

3. **Optimize for demo:**
   - Pre-load some example images
   - Have cURL commands ready to test backend
   - Test from different devices before presentation

---

**Need help deploying? Let me know which platform you choose!**
