# Dockerfile
# Packages our entire app into a container
 
# Start with Python 3.11 slim
FROM python:3.11-slim
 
# Set working directory
WORKDIR /app
 
# Copy requirements first
COPY requirements.txt .
 
# Install Python libraries
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy all project code
COPY . .
 
# Expose ports
EXPOSE 8501
EXPOSE 8000
# Start Streamlit using Railway's PORT variable
CMD sh -c "streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 
--server.headless true"