# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY yars.py .
COPY config.py .
COPY utils.py .
COPY src.py .

# Set the entrypoint
CMD ["python", "src.py"]
