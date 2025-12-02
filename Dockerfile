FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy pre-trained ML models and inference code (training done separately)
COPY backend/ml_models/ ./ml_models/
COPY backend/ml_pipeline/ ./ml_pipeline/

# Build frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci

COPY frontend/ .
RUN VITE_API_URL='' npm run build

# Move built frontend to static folder
WORKDIR /app
RUN mv frontend/dist static

EXPOSE 5001

CMD ["python", "app.py"]
