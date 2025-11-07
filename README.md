# 🍳 Meal Plan App

An AI-powered meal planning application that detects ingredients from photos using **YOLOv8** and generates personalized recipes using **OpenAI GPT**. Built with Flask (Python) backend and React + TypeScript frontend with a premium gold luxury design.

## ✨ Features

- 📸 **Photo Upload**: Take or upload photos of your ingredients
- 🤖 **AI Ingredient Detection**: Free, self-hosted YOLOv8 model (trainable on your own data!)
- 🍽️ **Recipe Generation**: OpenAI GPT-3.5-turbo generates custom recipes
- 💎 **Premium UI**: Glassmorphic design with gold accents and smooth animations
- 🎓 **Custom Training**: Train your own ingredient detector with your images (100% free!)

## 📋 Project Structure

```
Meal-Plan-App/
├── backend/                  # Flask API Server
│   ├── app.py               # Main Flask application
│   ├── openai_service.py    # OpenAI integration
│   ├── recipe_generator.py  # Recipe generation logic
│   └── requirements.txt     # Python dependencies
├── frontend/                # React + TypeScript App
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   ├── App.css         # Styling
│   │   └── main.tsx        # Entry point
│   ├── vite.config.ts      # Vite configuration
│   └── package.json        # Node dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API Key

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

## 🎓 Development Notes

This is a senior project with planned features:

- **Current:** Using mock ingredient detection
- **Future:** Integrate Ultralytics for image-based ingredient detection
- **Deployment:** Ready for platforms like Render, Heroku, or Vercel

## 📝 Scripts

**Backend:**
```bash
python app.py          # Run Flask server
```

**Frontend:**
```bash
npm run dev           # Start development server
npm run build         # Build for production
npm run preview       # Preview production build
```

## 🤝 Contributing

This is a college senior project. Feel free to fork and experiment!

## 📄 License

MIT License - feel free to use this for your own projects!