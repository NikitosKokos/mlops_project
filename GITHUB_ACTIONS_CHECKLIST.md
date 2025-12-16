# GitHub Actions Setup Checklist

## ✅ Pre-Setup Verification (Already Done!)

- [x] Azure ML Workspace exists: `sentinel-ml-workspace`
- [x] Compute cluster exists: `cpu-cluster`
- [x] Dataset uploaded: `gun-dataset` (v1)
- [x] Environment created: `ultralytics-env` (v2)
- [x] AKS cluster exists: `sentinel-aks`
- [x] GitHub Actions workflow file exists
- [x] Workflow location updated to match workspace

## 🔑 Required Setup Steps

### Step 1: Create Azure Service Principal ⚠️ REQUIRED

**⚠️ IMPORTANT for Git Bash on Windows:** Use `MSYS_NO_PATHCONV=1` to prevent path conversion errors.

**Run this command:**

```bash
# Git Bash on Windows (use MSYS_NO_PATHCONV=1):
MSYS_NO_PATHCONV=1 az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth

# PowerShell/CMD (no MSYS_NO_PATHCONV needed):
az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth
```

**Or use the setup script:**
- Windows: `setup_github_actions.bat`
- Linux/Mac: `bash setup_github_actions.sh`

**Output:** Copy the entire JSON response!

**If you get errors:** See [FIX_SERVICE_PRINCIPAL.md](FIX_SERVICE_PRINCIPAL.md)

### Step 2: Add GitHub Secret ⚠️ REQUIRED

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   - **Name:** `AZURE_CREDENTIALS`
   - **Value:** Paste the JSON from Step 1
5. Click **"Add secret"**

### Step 3: Verify Repository Settings

1. Go to: **Settings** → **Actions** → **General**
2. Under **"Workflow permissions"**:
   - Select: **"Read and write permissions"**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**

### Step 4: Test the Workflow

**Option A: Push to main branch**
```bash
git add .
git commit -m "Setup GitHub Actions"
git push origin main
```

**Option B: Create test branch**
```bash
git checkout -b test-github-actions
git add .
git commit -m "Test GitHub Actions workflow"
git push origin test-github-actions
# Create PR to main
```

## 📊 Workflow Status

After pushing, check:

1. Go to: **Actions** tab in GitHub
2. You should see: **"MLOps Sentinel Pipeline"** workflow
3. Click on it to see progress

## 🔍 Verification Commands

After setup, verify everything works:

```bash
# Check service principal exists
az ad sp list --display-name "sentinel-github-actions"

# Verify Azure resources
az ml workspace show --name sentinel-ml-workspace --resource-group sentinel-mlops-rg
az ml compute show --name cpu-cluster
az ml data show --name gun-dataset --version 1
az ml environment show --name ultralytics-env --version 2
az aks show --name sentinel-aks --resource-group sentinel-mlops-rg
```

## ⏱️ Expected Timeline

- **First workflow run:** 30-45 minutes
  - Training: ~20-30 minutes (20 epochs)
  - Model download: ~1-2 minutes
  - Docker build: ~5-10 minutes
  - K8s deploy: ~2-5 minutes

- **Subsequent runs:** 25-35 minutes (faster due to caching)

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "Authentication failed" | Check `AZURE_CREDENTIALS` secret format |
| "Compute not found" | Workflow creates it automatically |
| "Model not found" | Wait for training job to complete first |
| "Docker push failed" | Check repository permissions |
| "K8s deploy failed" | Verify AKS cluster is running |

## 📝 Files Created/Updated

- ✅ `.github/workflows/mlops-pipeline.yaml` - Updated location
- ✅ `GITHUB_ACTIONS_SETUP.md` - Comprehensive guide
- ✅ `QUICK_SETUP_GITHUB_ACTIONS.md` - Quick reference
- ✅ `setup_github_actions.sh` - Setup script (Linux/Mac)
- ✅ `setup_github_actions.bat` - Setup script (Windows)
- ✅ `GITHUB_ACTIONS_CHECKLIST.md` - This file

## 🎯 Next Steps

1. [ ] Create service principal (Step 1)
2. [ ] Add GitHub secret (Step 2)
3. [ ] Verify repository settings (Step 3)
4. [ ] Push to main and watch workflow (Step 4)
5. [ ] Monitor first run in Actions tab
6. [ ] Verify deployment in AKS

## 📚 Documentation

- **Quick Start:** [QUICK_SETUP_GITHUB_ACTIONS.md](QUICK_SETUP_GITHUB_ACTIONS.md)
- **Full Guide:** [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- **This Checklist:** [GITHUB_ACTIONS_CHECKLIST.md](GITHUB_ACTIONS_CHECKLIST.md)

---

**Ready to go!** Once you complete Steps 1-2, you can push to main and the workflow will run automatically! 🚀

