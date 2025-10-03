FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for pandas/numpy
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Make sure uploads folder exists
RUN mkdir -p /app/uploads

# Expose the Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
