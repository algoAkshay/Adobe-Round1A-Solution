FROM python:3.11-slim
WORKDIR /app

# The system dependencies for pdfplumber's dependencies are good to have
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Use --no-cache-dir to keep the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application code
COPY process.py .

# We will mount input and output directories as volumes at runtime,
# so we do not copy them into the image.

CMD ["python", "process.py"]