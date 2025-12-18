# Meal Plan App Local Setup Instructions

## Python Version Disclaimer
This project requires **Python 3.12**. It does not work with Python 3.13 or later due to compatibility issues with Pillow library.

---

## Backend Setup (Flask API)

### On macOS/Linux:
1. **Install Python 3.12** (if not already installed):
   ```sh
   brew install python@3.12
   ```
2. **Create and use the virtual environment:**
   ```sh
   cd backend
   python3.12 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up your .env file:**
   - Insert private .env file in the root of /backend.
5. **Start the backend server:**
   ```sh
   python app.py
   ```
   The backend will run on http://localhost:5001 by default.

### On Windows:
1. **Download and install Python 3.12** from https://www.python.org/downloads/release/python-3120/
2. **Create and use the virtual environment:**
   ```bat
   cd backend
   py -3.12 -m venv venv
   venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bat
   pip install -r requirements.txt
   ```
4. **Set up your .env file:**
   - Insert private .env file in the root of /backend.
5. **Start the backend server:**
   ```bat
   python app.py
   ```
   The backend will run on http://localhost:5001 by default.

---

## Start the frontend

1. **Open a new terminal window/tab.**
2. **Go to the frontend folder directory:**
   ```sh
   cd frontend
   ```
3. **Install dependencies:**
   ```sh
   npm install
   ```
4. **Start the frontend dev server:**
   ```sh
   npm run dev
   ```
   The frontend will run on http://localhost:3000 by default.

---

**Note:** The path to your virtual environment (venv) can vary based on operating system and Python installation. Please make sure you are using Python 3.12 and in the backend directory when establishing a new virtual environment, activating it, and installing dependencies. The frontend requires installing Node.js (which has npm) to be installed on the local system.


