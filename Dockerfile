FROM python:3.12-slim

WORKDIR /app

# rasterio (map tool) needs libexpat, missing in the slim image
RUN apt-get update && apt-get install -y --no-install-recommends libexpat1 && rm -rf /var/lib/apt/lists/*

# CPU-only torch + torchvision (must match) keeps the image much smaller
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
WORKDIR /app/src

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]
