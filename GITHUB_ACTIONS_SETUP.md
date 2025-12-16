# GitHub Actions Setup Plan

## ✅ Current Azure Resources Status

Based on your Azure setup, here's what you already have:

| Resource               | Status    | Details                                        |
| ---------------------- | --------- | ---------------------------------------------- |
| **Azure ML Workspace** | ✅ Exists | `sentinel-ml-workspace` in `sentinel-mlops-rg` |
| **Compute Cluster**    | ✅ Exists | `cpu-cluster`                                  |
| **Dataset**            | ✅ Exists | `gun-dataset` (version 1)                      |
| **Environment**        | ✅ Exists | `ultralytics-env` (version 2)                  |
| **AKS Cluster**        | ✅ Exists | `sentinel-aks` (Running)                       |
| **Models**             | ⚠️ Check  | Need to verify if any models are registered    |

## 📋 Pre-Flight Checklist

### Step 1: Verify Azure Resources ✅

All required Azure resources are already set up! You can verify with:

```bash
# Verify workspace
az ml workspace show --name sentinel-ml-workspace --resource-group sentinel-mlops-rg

# Verify compute
az ml compute show --name cpu-cluster

# Verify dataset
az ml data show --name gun-dataset --version 1

# Verify environment
az ml environment show --name ultralytics-env --version 2

# Verify AKS
az aks show --name sentinel-aks --resource-group sentinel-mlops-rg
```

### Step 2: Create Azure Service Principal for GitHub Actions 🔑

**This is the most critical step!**

**⚠️ IMPORTANT for Git Bash on Windows:** Use `MSYS_NO_PATHCONV=1` to prevent path conversion issues.

```bash
# Set variables from your .env
RESOURCE_GROUP="sentinel-mlops-rg"
SUBSCRIPTION_ID="caea5300-fef2-4d0e-b763-d1d328c33974"

# Create service principal with contributor role
# For Git Bash on Windows, use MSYS_NO_PATHCONV=1
MSYS_NO_PATHCONV=1 az ad sp create-for-rbac \
  --name "sentinel-github-actions" \
  --role contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
  --sdk-auth
```

**Alternative (PowerShell/CMD):**

```powershell
az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth
```

**⚠️ IMPORTANT:** Copy the entire JSON output! It will look like:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  ...
}
```

### Step 3: Add GitHub Secrets 🔐

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add the following secret:
   -  **Name:** `AZURE_CREDENTIALS`
   -  **Value:** Paste the entire JSON output from Step 2

**Note:** `GITHUB_TOKEN` is automatically provided by GitHub Actions, no need to add it.

### Step 4: Fix GitHub Actions Workflow 🛠️

I noticed a small issue in your workflow file. Let me fix it:

**Issue:** Missing `uses:` in the docker login step (line 64)

The workflow needs to be updated. I'll fix this for you.

### Step 5: Verify Workflow Configuration ✅

Check these values in `.github/workflows/mlops-pipeline.yaml`:

-  ✅ `GROUP: 'sentinel-mlops-rg'` - Matches your resource group
-  ✅ `WORKSPACE: 'sentinel-ml-workspace'` - Matches your workspace
-  ⚠️ `LOCATION: 'westeurope'` - **Check if this matches your actual location**

Your workspace is in `germanywestcentral` (from the discovery URL), but workflow says `westeurope`. This might need adjustment.

### Step 6: Update Kubernetes Deployment 🚀

The `k8s/deployment.yaml` has a placeholder. The workflow will automatically replace it, but verify the image path format is correct.

### Step 7: Test the Workflow 🧪

**Option A: Test with a test workflow first**

Create a simple test to verify Azure connection:

```yaml
name: Test Azure Connection
on: [workflow_dispatch]
jobs:
   test:
      runs-on: ubuntu-latest
      steps:
         - uses: actions/checkout@v4
         - uses: azure/login@v2
           with:
              creds: ${{ secrets.AZURE_CREDENTIALS }}
         - run: |
              az extension add -n ml -y
              az ml workspace show --name sentinel-ml-workspace --resource-group sentinel-mlops-rg
```

**Option B: Push to main branch**

The workflow triggers on push to `main` branch. Make a small change and push:

```bash
git checkout -b test-github-actions
# Make a small change (e.g., update README)
git add .
git commit -m "Test GitHub Actions workflow"
git push origin test-github-actions
# Create PR to main, or merge directly
```

## 🔍 Troubleshooting Common Issues

### Issue 1: "Authentication failed"

-  **Solution:** Verify `AZURE_CREDENTIALS` secret is correctly formatted JSON
-  **Check:** Service principal has contributor role on resource group

### Issue 2: "Compute cluster not found"

-  **Solution:** The workflow creates it if missing, but verify it exists:
   ```bash
   az ml compute show --name cpu-cluster
   ```

### Issue 3: "Dataset not found"

-  **Solution:** Verify dataset is uploaded:
   ```bash
   az ml data show --name gun-dataset --version 1
   ```

### Issue 4: "Environment not found"

-  **Solution:** Your environment is version 2, but workflow might reference version 1
-  **Check:** `components/training/training.yaml` uses `ultralytics-env:2` ✅

### Issue 5: "AKS cluster not found"

-  **Solution:** Verify AKS exists and is running:
   ```bash
   az aks show --name sentinel-aks --resource-group sentinel-mlops-rg
   ```

### Issue 6: "Docker image push failed"

-  **Solution:** Verify GitHub Container Registry permissions
-  **Check:** Repository settings → Actions → General → Workflow permissions → Read and write permissions

## 📝 Quick Setup Commands

Here's a complete script to set up everything:

```bash
#!/bin/bash
# Complete GitHub Actions Setup Script

RESOURCE_GROUP="sentinel-mlops-rg"
SUBSCRIPTION_ID="caea5300-fef2-4d0e-b763-d1d328c33974"
WORKSPACE="sentinel-ml-workspace"

echo "Step 1: Creating service principal..."
SP_OUTPUT=$(az ad sp create-for-rbac \
  --name "sentinel-github-actions" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth)

echo ""
echo "=========================================="
echo "COPY THIS JSON TO GITHUB SECRETS:"
echo "=========================================="
echo "$SP_OUTPUT"
echo ""
echo "Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo "Add secret: AZURE_CREDENTIALS"
echo "Paste the JSON above"
echo "=========================================="

echo ""
echo "Step 2: Verifying Azure resources..."
az ml workspace show --name $WORKSPACE --resource-group $RESOURCE_GROUP --query "name" -o tsv
az ml compute show --name cpu-cluster --query "name" -o tsv
az ml data show --name gun-dataset --version 1 --query "name" -o tsv
az ml environment show --name ultralytics-env --version 2 --query "name" -o tsv
az aks show --name sentinel-aks --resource-group $RESOURCE_GROUP --query "name" -o tsv

echo ""
echo "✅ Setup complete! Add the service principal JSON to GitHub secrets."
```

## 🎯 Next Steps

1. ✅ **Create service principal** (Step 2)
2. ✅ **Add GitHub secret** (Step 3)
3. ✅ **Fix workflow file** (I'll do this)
4. ✅ **Test workflow** (Step 7)

## 📊 Workflow Overview

Your GitHub Actions workflow does the following:

1. **Train and Register Job:**

   -  Logs into Azure
   -  Creates/starts compute cluster
   -  Runs training pipeline
   -  Registers model (via pipeline-job.yaml)

2. **Build and Deploy Job:**
   -  Downloads registered model
   -  Builds Docker image
   -  Pushes to GitHub Container Registry
   -  Deploys to AKS cluster

## ⚠️ Important Notes

1. **Location Mismatch:** Your workspace is in `germanywestcentral` but workflow uses `westeurope`. The workflow should still work, but consider updating for consistency.

2. **Model Registration:** The `pipeline-job.yaml` includes a model registration step. Make sure this works correctly.

3. **First Run:** The first workflow run might take 20-30 minutes (training + build + deploy).

4. **Costs:** Be aware that:
   -  Compute cluster costs while training
   -  AKS cluster costs while running
   -  Storage costs for models and datasets

## 🚀 Ready to Go!

Once you've:

1. Created the service principal
2. Added the GitHub secret
3. Fixed the workflow (I'll do this)

You can push to `main` branch and watch the magic happen! 🎉
