# 🍳 Meal Plan App

An AI-powered meal planning application that detects ingredients from photos using **Grounded-SAM computer vision** and generates personalized recipes using **OpenAI GPT**. Built with Flask (Python) backend and React + TypeScript frontend with a premium gold luxury design.

## ✨ Features

- 📸 **Photo Upload**: Take or upload photos of your ingredients
- 🤖 **AI Ingredient Detection**: Grounded-SAM (Grounding DINO + Segment Anything)
- 🍽️ **Recipe Generation**: OpenAI GPT generates custom recipes based on detected ingredients
- 💎 **Premium UI**: Glassmorphic design with gold accents and smooth animations
-  **Zero-Shot Detection**: Detects ANY food item without training!

## �️ Tech Stack

- **Backend**: Flask (Python), Grounded-SAM, OpenAI API
- **Frontend**: React, TypeScript, Vite, Framer Motion
- **Deployment**: Docker, Railway/Render (backend), Vercel (frontend)

## 📋 Project Structure

```
Meal-Plan-App/
├── backend/                     # Flask API Server
│   ├── app.py                  # Main Flask application
│   ├── grounded_sam_service.py # Computer vision service
│   ├── openai_service.py       # OpenAI integration
│   ├── recipe_generator.py     # Recipe generation logic
│   ├── requirements.txt        # Python dependencies
│   └── models/grounded_sam/    # AI model files
├── frontend/                    # React + TypeScript App
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   └── App.tsx            # Main app
│   └── package.json
├── Dockerfile                   # Backend deployment config
├── start.sh                     # Local startup script
└── deploy.sh                    # Deployment helper
```

## 🚀 Quick Start (Local Development)

**⚡ Want to get started in 3 minutes?** See **[QUICKSTART.md](QUICKSTART.md)** for the fastest setup!

**Or use the quick start script:**
```bash
./quickstart.sh  # Automated setup and startup
```

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - Flask & Flask-CORS (API server)
   - OpenAI (recipe generation)
   - **Ultralytics YOLOv8** (ingredient detection) 🆕
   - Pillow & OpenCV (image processing) 🆕

4. **Create `.env` file in backend/ directory:**
   ```env
   OPENAI_API_KEY=your_api_key_here
   PORT=5000
   HOST=127.0.0.1
   FLASK_DEBUG=true
   ```

5. **Test YOLOv8 detection (optional):**
   ```bash
   python test_detection.py
   ```
   
   This verifies YOLOv8 is working and shows what it can detect!

6. **Run the Flask server:**
   ```bash
   python app.py
   ```
   
   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:3000`

## � Training Your Own Model

Want to detect YOUR ingredients? See **[TRAINING_GUIDE.md](TRAINING_GUIDE.md)** for the complete guide!

**Quick overview:**
1. Collect 100-500 images of ingredients
2. Label them using Roboflow (free)
3. Train YOLOv8 on your images (free!)
4. Deploy your custom model

**Pre-trained model** already detects: apple, banana, orange, broccoli, carrot, and more!

## 🛠️ Tech Stack

**Backend:**
- Flask 2.3 - Python web framework
- **YOLOv8 (Ultralytics)** - FREE ingredient detection 🆕
- OpenAI GPT-3.5-turbo - Recipe generation
- PyTorch - Deep learning framework
- Pillow & OpenCV - Image processing
- Flask-CORS - Cross-origin support

**Frontend:**
- React 18 - UI library
- TypeScript - Type safety
- Vite 7 - Lightning-fast build tool
- Framer Motion - Smooth animations
- CSS3 - Glassmorphism with gold accents

## 📡 API Endpoints

### `POST /detect-ingredients` 🆕
Detects ingredients from uploaded image using YOLOv8.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "status": "success",
  "ingredients": ["apple", "banana", "broccoli"]
}
```

### `POST /generate-recipes`
Generates recipes based on detected/provided ingredients using OpenAI.

**Request:**
```json
{
  "ingredients": ["chicken", "broccoli", "rice"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "ingredients": ["chicken", "broccoli", "rice"],
    "recipes": [
      {
        "title": "Chicken Broccoli Stir Fry",
        "meal_type": "dinner",
        "ingredients": ["2 chicken breasts", "1 cup broccoli", "1 cup rice"],
        "steps": ["Cook rice", "Stir fry chicken", "Add broccoli", "Serve"]
      }
    ]
  }
}
```

## 🚀 Deployment

### Test First

```bash
./check.sh
./test-docker.sh
```

If `test-docker.sh` passes, deployment will work.

---

### Quick Deploy

```bash
./deploy.sh
```

### Railway (Recommended)

1. Push to GitHub
2. Connect repo on [railway.app](https://railway.app)
3. Add environment variable: `OPENAI_API_KEY`
4. Deploy

### Render

1. Push to GitHub
2. Create new Blueprint on [render.com](https://render.com)
3. Connect repo (uses `render.yaml`)
4. Add environment variable: `OPENAI_API_KEY`

### Docker (Self-host)

```bash
docker build -t meal-plan-backend .
docker run -p 5001:5001 -e OPENAI_API_KEY=key meal-plan-backend
```

**📖 Full guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📝 Scripts

**Start app:**
```bash
./start.sh
```

**Backend:**
```bash
cd backend
python app.py
```

**Frontend:**
```bash
cd frontend
npm run dev
npm run build
```

## 🐛 Troubleshooting

### Backend won't start

1. **Check if `.env` file exists:**
   ```bash
   ls backend/.env
   ```
   If not found, copy from example:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Then edit `backend/.env` and add your OpenAI API key.

2. **Check Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Check if port 5001 is already in use:**
   ```bash
   lsof -ti :5001
   # Kill existing process:
   lsof -ti :5001 | xargs kill -9
   ```

4. **View backend logs:**
   ```bash
   tail -f /tmp/meal-plan-backend.log
   ```

### Frontend won't start

1. **Check Node dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Check if port 3000 is already in use:**
   ```bash
   lsof -ti :3000
   # Kill existing process:
   lsof -ti :3000 | xargs kill -9
   ```

3. **View frontend logs:**
   ```bash
   tail -f /tmp/meal-plan-frontend.log
   ```

### Port mismatch issues

Ensure these match:
- `backend/app.py` default port: **5001**
- `frontend/vite.config.ts` proxy target: **http://localhost:5001**
- `frontend/src/components/api.ts` BASE_URL: **http://localhost:5001**

### Models taking too long to load

The Grounded-SAM models are large and can take 10-20 seconds to load on CPU. Wait for:
```
[grounded_sam_service] 🎉 Service ready! Detecting 52 food categories
```

### OpenAI API errors

1. Check your API key is set in `backend/.env`
2. Check your OpenAI account has credits: https://platform.openai.com/account/usage
3. Check API endpoint in logs for specific error messages

## 📝 Scripts

**Start app:**
```bash
./start.sh
```

**Backend:**
```bash
cd backend
python app.py
```

**Frontend:**
```bash
cd frontend
npm run dev
npm run build
```

## 🤝 Contributing

This is a college senior project. Feel free to fork and experiment!

## 📄 License

MIT License - feel free to use this for your own projects!