# Quick Setup Guide - GitHub Actions

## 🚀 Fast Track (5 minutes)

### Step 1: Create Azure Service Principal

**⚠️ For Git Bash on Windows:** Use `MSYS_NO_PATHCONV=1` to fix path issues.

```bash
# Using the setup script (recommended)
setup_github_actions.bat

# Or manually (Git Bash):
MSYS_NO_PATHCONV=1 az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth

# Or use PowerShell/CMD (no MSYS_NO_PATHCONV needed):
az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth
```

**Copy the JSON output!** See [FIX_SERVICE_PRINCIPAL.md](FIX_SERVICE_PRINCIPAL.md) if you get errors.

### Step 2: Add GitHub Secret

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **"New repository secret"**
3. Name: `AZURE_CREDENTIALS`
4. Value: Paste the JSON from Step 1
5. Click **"Add secret"**

### Step 3: Test the Workflow

**Option A: Push to main**
```bash
git add .
git commit -m "Test GitHub Actions"
git push origin main
```

**Option B: Create a test branch**
```bash
git checkout -b test-actions
git add .
git commit -m "Test GitHub Actions"
git push origin test-actions
# Then merge to main via PR
```

## ✅ What's Already Set Up

- ✅ Azure ML Workspace: `sentinel-ml-workspace`
- ✅ Compute Cluster: `cpu-cluster`
- ✅ Dataset: `gun-dataset` (v1)
- ✅ Environment: `ultralytics-env` (v2)
- ✅ AKS Cluster: `sentinel-aks`
- ✅ GitHub Actions Workflow: `.github/workflows/mlops-pipeline.yaml`

## 🔍 Verify Setup

Check if everything is ready:

```bash
# Verify Azure resources
az ml workspace show --name sentinel-ml-workspace --resource-group sentinel-mlops-rg
az ml compute show --name cpu-cluster
az ml data show --name gun-dataset --version 1
az ml environment show --name ultralytics-env --version 2
az aks show --name sentinel-aks --resource-group sentinel-mlops-rg
```

## 📋 Workflow Overview

When you push to `main`, the workflow will:

1. **Train Model** (Job 1):
   - Login to Azure
   - Start compute cluster
   - Run training pipeline (20 epochs)
   - Register model as `gun-detection-yolo`

2. **Deploy Model** (Job 2):
   - Download registered model
   - Build Docker image
   - Push to GitHub Container Registry
   - Deploy to AKS cluster

**Total time:** ~30-45 minutes (first run)

## ⚠️ Important Notes

1. **Location:** Updated to `germanywestcentral` to match your workspace
2. **Model Registration:** Happens automatically in the pipeline
3. **First Run:** May take longer due to compute startup
4. **Costs:** Compute and AKS will incur charges while running

## 🐛 Troubleshooting

**Workflow fails at "Azure Login":**
- Check `AZURE_CREDENTIALS` secret is correct JSON
- Verify service principal has contributor role

**Workflow fails at "Download Model":**
- Check if model was registered (first job must complete)
- Verify model name: `gun-detection-yolo`

**Workflow fails at "Deploy to Kubernetes":**
- Verify AKS cluster is running
- Check kubectl credentials

## 📚 More Details

See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for comprehensive guide.

