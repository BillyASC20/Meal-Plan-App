FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir git+https://github.com/IDEA-Research/GroundingDINO.git
RUN pip install --no-cache-dir git+https://github.com/facebookresearch/segment-anything.git

COPY backend/ .

RUN mkdir -p models/grounded_sam

RUN python -c "import urllib.request; \
    urllib.request.urlretrieve('https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth', 'models/grounded_sam/groundingdino_swint_ogc.pth'); \
    urllib.request.urlretrieve('https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth', 'models/grounded_sam/sam_vit_b_01ec64.pth')"

COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci

COPY frontend/ .
RUN VITE_API_URL='' npm run build

WORKDIR /app
RUN mv frontend/dist static

EXPOSE 5001

CMD ["python", "app.py"]
