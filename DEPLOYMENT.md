# Deployment Guide for Meal Plan App Backend

## 🚀 Quick Deploy Options

Your backend is ready to deploy on multiple platforms. Choose one:

---

## Option 1: Railway (Recommended - Easiest)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `Meal-Plan-App` repository
   - Railway will auto-detect the Dockerfile
   - Add environment variable: `OPENAI_API_KEY=your_key_here`
   - Deploy!

3. **Get your URL:**
   - Railway will give you a URL like `https://meal-plan-backend.railway.app`
   - Update your frontend `api.ts` with this URL

**Pros:** Free tier, automatic HTTPS, easy setup
**Build time:** ~10-15 minutes (downloads models during build)

---

## Option 2: Render

1. **Push to GitHub** (same as above)

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repo
   - Render will use `render.yaml` config
   - Add environment variable: `OPENAI_API_KEY`
   - Deploy!

**Pros:** Free tier available, good for production
**Build time:** ~10-15 minutes

---

## Option 3: Docker (Self-hosted / Any platform)

1. **Build the image:**
   ```bash
   docker build -t meal-plan-backend .
   ```

2. **Run locally:**
   ```bash
   docker run -p 5001:5001 -e OPENAI_API_KEY=your_key_here meal-plan-backend
   ```

3. **Deploy to any Docker host:**
   - DigitalOcean App Platform
   - AWS ECS
   - Google Cloud Run
   - Azure Container Apps

---

## Frontend Deployment (Vercel)

Already configured in `frontend/vercel.json`:

1. **Deploy frontend:**
   ```bash
   cd frontend
   vercel
   ```

2. **Update API URL:**
   - After backend is deployed, update `frontend/src/components/api.ts`
   - Change `BASE_URL` to your backend URL
   - Redeploy: `vercel --prod`

---

## Environment Variables Needed

### Backend:
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `PORT` - Port number (default: 5001)
- `FLASK_DEBUG` - Set to `false` for production

### Frontend:
- No environment variables needed (API URL is in code)

---

## Model Files

The Dockerfile automatically downloads:
- Grounding DINO model (~662MB)
- SAM base model (~375MB)

**Total deployment size:** ~2.5GB
**First build time:** 10-15 minutes
**Subsequent builds:** 2-3 minutes (cached)

---

## Testing Deployment

After deployment, test your backend:

```bash
curl https://your-backend-url.com/health
```

Should return: `{"status": "healthy", "service": "ready"}`

---

## Cost Estimates

- **Railway:** Free tier (500hrs/month, sleeps after inactivity)
- **Render:** Free tier (750hrs/month, spins down after 15min)
- **Vercel (frontend):** Free tier (unlimited)

**Recommended for production:** Railway Hobby ($5/mo) or Render Starter ($7/mo)

---

## Quick Commands

```bash
# Test Docker locally
docker build -t meal-plan-backend .
docker run -p 5001:5001 -e OPENAI_API_KEY=$OPENAI_API_KEY meal-plan-backend

# Deploy to Railway (after connecting repo)
railway up

# Deploy frontend to Vercel
cd frontend && vercel --prod
```

---

## Notes

- ⏱️ **Cold starts:** First request may take 10-30s (models loading)
- 💾 **Memory usage:** ~2GB RAM needed
- 🔒 **CORS:** Currently allows all origins (update in production)
- 📦 **Models:** Baked into Docker image (no runtime downloads)
