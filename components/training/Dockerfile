# Use Azure ML base image
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

# Install system dependencies required by OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libgomp1 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to help with library loading
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}
