# Use Python 3.10 as the base (best for PaddleOCR)
FROM python:3.10-slim

# Install ALL Linux system dependencies in one step
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libgomp1 \
    ca-certificates \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download detector model so startup does not rely on runtime cache paths
RUN mkdir -p /opt/models \
    && curl -fL "https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar" -o /tmp/en_PP-OCRv3_det_infer.tar \
    && tar -xf /tmp/en_PP-OCRv3_det_infer.tar -C /opt/models \
    && rm -f /tmp/en_PP-OCRv3_det_infer.tar

# Point backend to detector model in the image
ENV DET_MODEL_DIR=/opt/models/en_PP-OCRv3_det_infer

# Copy the rest of your code (including your models and dict files)
COPY . .

# Expose the port Render uses
EXPOSE 8000

# Start command
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
