# Dockerfile
# Packages our entire app into a container

# ─────────────────────────────────────
# Start with Python 3.11 slim
# ─────────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ─────────────────────────────────────
# Copy requirements first
# Docker caches this layer
# Only reinstalls if requirements change
# ─────────────────────────────────────
COPY requirements.txt .

# ─────────────────────────────────────
# Install Python libraries
# ─────────────────────────────────────
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────
# Copy all project code
# ─────────────────────────────────────
COPY . .

# ─────────────────────────────────────
# Expose ports
# 8501 = Streamlit
# 8000 = FastAPI
# ─────────────────────────────────────
EXPOSE 8501
EXPOSE 8000

# ─────────────────────────────────────
# Start Streamlit when container runs
# ─────────────────────────────────────
CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]