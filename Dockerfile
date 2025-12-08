# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in stages to avoid conflicts
# Stage 1: Install numpy first (many packages depend on it)
RUN pip install --no-cache-dir numpy>=1.24.0

# Stage 2: Install PyTorch (large package, install separately)
RUN pip install --no-cache-dir torch>=2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Stage 3: Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run the Streamlit app
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true", "--browser.serverAddress=0.0.0.0", "--browser.gatherUsageStats=false"]
