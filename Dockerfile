# Base image with Python 3.6
FROM python:3.6-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies for building some packages
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["bash"]
