# SentinelAI - Automated Gun Detection System

A comprehensive MLOps project for real-time weapon detection using YOLOv8, Azure Machine Learning, FastAPI, and Kubernetes.

## Project Overview

SentinelAI is designed for a smart security startup. The system processes video feeds from security cameras and automatically triggers alerts when firearms are detected with high confidence.

### Key Components

-  **AI Model**: YOLOv8 (nano version) for real-time object detection
-  **Training**: Azure Machine Learning Service with automated pipelines
-  **API**: FastAPI microservice for inference
-  **Deployment**: Kubernetes for scalable, self-healing deployment
-  **CI/CD**: GitHub Actions for automated training and deployment

## Project Structure

```
sentinel-mlops/
├── components/
│   └── training/
│       ├── train.py              # Training script
│       ├── training.yaml         # Azure ML component definition
│       └── environment.yml       # Conda environment for Azure ML
├── inference/
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Container image definition
├── k8s/
│   └── deployment.yaml           # Kubernetes deployment manifest
├── .github/
│   └── workflows/
│       └── mlops-pipeline.yaml   # CI/CD pipeline
├── pipeline-job.yaml             # Azure ML pipeline definition
└── README.md                     # This file
```

## Prerequisites

-  Azure subscription with appropriate permissions
-  Azure CLI installed and configured
-  Docker installed
-  Kubernetes cluster (AKS or local Minikube)
-  GitHub account with repository
-  Kaggle account (for dataset access)

## Azure Setup Guide

Follow these steps to set up your Azure environment for this project.

### Step 1: Install Azure CLI and Extensions

```bash
# Install Azure CLI (if not already installed)
# Windows: Download from https://aka.ms/installazurecliwindows
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Install Azure ML extension
az extension add -n ml

# Verify installation
az ml --help
```

### Step 2: Create Resource Group and Azure ML Workspace

```bash
# Set variables (replace with your values)
RESOURCE_GROUP="sentinel-mlops-rg"
LOCATION="eastus"  # or your preferred region
WORKSPACE_NAME="sentinel-ml-workspace"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure ML workspace
az ml workspace create \
  --name $WORKSPACE_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 3: Create Compute Cluster

```bash
# Configure defaults
az configure --defaults group=$RESOURCE_GROUP workspace=$WORKSPACE_NAME location=$LOCATION

# Create compute cluster for training
az ml compute create \
  --name cpu-cluster \
  --size Standard_DS11_v2 \
  --min-instances 0 \
  --max-instances 2 \
  --type AmlCompute
```

### Step 4: Create Azure ML Environment

You need to create a custom environment for YOLOv8 training. You can do this via Azure ML Studio or CLI:

**Option A: Using Azure ML Studio**

1. Navigate to your Azure ML workspace in the Azure Portal
2. Go to "Environments" → "Create"
3. Name: `ultralytics-env`
4. Select "Use existing Docker image with conda"
5. Base image: `mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04`
6. Upload the `components/training/environment.yml` file
7. Create the environment

**Option B: Using Azure CLI**

```bash
# Create environment from conda file
az ml environment create \
  --name ultralytics-env \
  --image mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04 \
  --conda-file components/training/environment.yml \
  --version 1
```

### Step 5: Upload Dataset to Azure ML

1. **Download the Kaggle Dataset**

   -  Go to [Kaggle - Helmet and Gun Testing Dataset](https://www.kaggle.com/datasets/abuzarkhaaan/helmetandguntesting)
   -  Download the dataset (you'll need a Kaggle API token)
   -  Extract the dataset locally

2. **Prepare Dataset Structure**

   ```
   gun-dataset/
   ├── images/
   │   ├── train/
   │   └── val/
   └── labels/
       ├── train/
       └── val/
   ```

3. **Upload to Azure ML Data Assets**

   ```bash
   # Upload dataset as a folder
   az ml data create \
     --name gun-dataset \
     --type uri_folder \
     --path <path-to-your-dataset-folder> \
     --version 1
   ```

   Or use Azure ML Studio:

   -  Go to "Data" → "Data assets" → "Create"
   -  Name: `gun-dataset`
   -  Type: `URI folder`
   -  Select your dataset folder
   -  Create

### Step 6: Configure GitHub Secrets

1. **Get Azure Service Principal Credentials**

   ```bash
   # Create service principal for GitHub Actions
   az ad sp create-for-rbac \
     --name "sentinel-github-actions" \
     --role contributor \
     --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/$RESOURCE_GROUP \
     --sdk-auth
   ```

   Copy the JSON output - you'll need it for GitHub secrets.

2. **Add GitHub Secrets**
   -  Go to your GitHub repository
   -  Settings → Secrets and variables → Actions
   -  Add the following secrets:
      -  `AZURE_CREDENTIALS`: Paste the JSON output from step above
      -  Update workflow file with your values:
         -  `GROUP`: Your resource group name
         -  `WORKSPACE`: Your workspace name
         -  `LOCATION`: Your Azure region

### Step 7: Update Configuration Files

Before running the pipeline, update these files with your specific values:

1. **`.github/workflows/mlops-pipeline.yaml`**

   -  Replace `<YOUR_RESOURCE_GROUP>` with your resource group name
   -  Replace `<YOUR_WORKSPACE>` with your workspace name
   -  Replace `<YOUR_LOCATION>` with your Azure region

2. **`k8s/deployment.yaml`**

   -  Replace `<YOUR_GITHUB_USERNAME>` with your GitHub username

3. **`pipeline-job.yaml`**
   -  Verify the dataset name matches what you uploaded
   -  Adjust epochs if needed

### Step 8: Set Up Kubernetes Cluster

**Option A: Azure Kubernetes Service (AKS)**

```bash
# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name sentinel-aks \
  --node-count 2 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name sentinel-aks
```

**Option B: Local Minikube (for testing)**

```bash
# Install Minikube (if not installed)
# Windows: choco install minikube
# Mac: brew install minikube

# Start Minikube
minikube start

# Verify
kubectl get nodes
```

### Step 9: Configure Kubernetes Deployment

If using AKS, you may need to configure the GitHub Actions workflow to authenticate with your cluster. Add this step before the deploy step:

```yaml
- name: Configure kubectl
  run: |
     az aks get-credentials --resource-group ${{ env.GROUP }} --name sentinel-aks
```

Or set up a `KUBECONFIG` secret in GitHub with your cluster credentials.

## Running the Pipeline

### Manual Training (Azure ML CLI)

```bash
# Configure defaults
az configure --defaults group=$RESOURCE_GROUP workspace=$WORKSPACE_NAME location=$LOCATION

# Submit pipeline job
az ml job create --file pipeline-job.yaml --stream
```

### Automated CI/CD

1. Push code to the `main` branch
2. GitHub Actions will automatically:
   -  Train the model in Azure ML
   -  Register the model
   -  Download the model
   -  Build Docker image
   -  Deploy to Kubernetes

### Local Testing

```bash
# Test FastAPI locally
cd inference
pip install -r requirements.txt
# Place best.pt in this directory (download from Azure ML)
uvicorn main:app --reload

# Test API
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

## Monitoring and Troubleshooting

### Azure ML Studio

-  View pipeline runs: Azure ML Studio → Pipelines
-  Monitor training: Experiments → gun-detection-exp
-  Check registered models: Models → gun-detection-yolo

### Kubernetes

```bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/sentinel-api

# Check service endpoint
kubectl get service sentinel-service
```

### Common Issues

1. **Environment not found**: Ensure `ultralytics-env` is created with version 1
2. **Dataset not found**: Verify dataset name and version in `pipeline-job.yaml`
3. **Compute cluster not available**: Check cluster status in Azure ML Studio
4. **Docker build fails**: Ensure model file is downloaded before building
5. **Kubernetes deployment fails**: Verify image path and KUBECONFIG credentials

## API Documentation

Once deployed, access the API documentation at:

-  Swagger UI: `http://<your-service-ip>/docs`
-  ReDoc: `http://<your-service-ip>/redoc`

### API Endpoints

-  `GET /`: Health check
-  `POST /detect`: Upload image and get detection results

### Example Request

```bash
curl -X POST "http://<service-ip>/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

### Example Response

```json
{
   "filename": "image.jpg",
   "detections": [
      {
         "label": "gun",
         "confidence": 0.95,
         "box": [100, 150, 200, 250]
      }
   ],
   "alert": true
}
```

## Cost Optimization Tips

1. **Compute Cluster**: Set `min-instances: 0` to scale down when not in use
2. **Kubernetes**: Use spot instances for non-production workloads
3. **Model Storage**: Archive old model versions to reduce storage costs
4. **Monitoring**: Set up budget alerts in Azure

## Next Steps

-  Add model versioning and A/B testing
-  Implement model monitoring and drift detection
-  Add authentication to the API
-  Set up alerting for production incidents
-  Implement model retraining triggers based on performance metrics

## License

This project is for educational purposes as part of an MLOps course.

## Support

For issues or questions:

1. Check Azure ML Studio logs
2. Review GitHub Actions workflow logs
3. Check Kubernetes pod logs
4. Verify all secrets and configurations are correct
