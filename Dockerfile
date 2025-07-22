# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install required system packages for PyMuPDF
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libgl1-mesa-glx libxrender1 libsm6 libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the script into the container
COPY main.py ./main.py

# Create input/output folders
RUN mkdir -p input output

# Install Python libraries
RUN pip install pymupdf

# Run the app
CMD ["python", "main.py"]
