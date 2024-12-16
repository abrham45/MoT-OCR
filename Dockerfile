# Use a stable Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install additional dependencies for Tesseract
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-amh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose port and set the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
