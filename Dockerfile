FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install GroundingDINO and SAM from GitHub
RUN pip install --no-cache-dir git+https://github.com/IDEA-Research/GroundingDINO.git
RUN pip install --no-cache-dir git+https://github.com/facebookresearch/segment-anything.git

# Copy backend code
COPY backend/ .

# Create models directory
RUN mkdir -p models/grounded_sam

# Download models during build
RUN python -c "import urllib.request; \
    urllib.request.urlretrieve('https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth', 'models/grounded_sam/groundingdino_swint_ogc.pth'); \
    urllib.request.urlretrieve('https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth', 'models/grounded_sam/sam_vit_b_01ec64.pth')"

# Expose port
EXPOSE 5001

# Run the application
CMD ["python", "app.py"]
