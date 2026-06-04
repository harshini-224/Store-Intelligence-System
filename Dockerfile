FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install API and Pipeline dependencies
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY data/pipeline/ ./data/pipeline/
COPY yolo11n.pt ./yolo11n.pt

# Pre-create output directories so the API can read them at runtime
RUN mkdir -p data/outputs/analytics \
             data/outputs/tracking \
             data/outputs/events \
             data/outputs/conversion \
             data/outputs/heatmaps \
             data/outputs/metadata \
             data/outputs/detection

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
