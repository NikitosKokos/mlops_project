# This Dockerfile is for the training environment context
# The actual training runs on Azure ML compute, but this can be used for local testing

FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY ../components/training/environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Activate environment and install additional dependencies
SHELL ["conda", "run", "-n", "ultralytics-env", "/bin/bash", "-c"]

WORKDIR /workspace

