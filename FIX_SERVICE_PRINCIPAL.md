# Fix: Service Principal Creation Error

## Problem

When running the service principal creation command in Git Bash on Windows, you get this error:

```
ERROR: (MissingSubscription) The request did not have a subscription or a valid tenant level resource provider.
```

This happens because Git Bash converts `/subscriptions/...` to `C:/Program Files/Git/subscriptions/...`

## Solution

### Option 1: Use MSYS_NO_PATHCONV=1 (Recommended for Git Bash)

```bash
# Set variables
RESOURCE_GROUP="sentinel-mlops-rg"
SUBSCRIPTION_ID="caea5300-fef2-4d0e-b763-d1d328c33974"

# Create service principal with MSYS_NO_PATHCONV=1
MSYS_NO_PATHCONV=1 az ad sp create-for-rbac \
  --name "sentinel-github-actions" \
  --role contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
  --sdk-auth
```

### Option 2: Use PowerShell or CMD

Open PowerShell or CMD (not Git Bash) and run:

```powershell
az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth
```

### Option 3: Use Azure Cloud Shell

1. Go to https://shell.azure.com
2. Run the command directly (no path conversion issues)

## Verify It Worked

After running the command, you should see JSON output like:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "caea5300-fef2-4d0e-b763-d1d328c33974",
  "tenantId": "...",
  ...
}
```

**⚠️ IMPORTANT:** Copy this entire JSON output - you'll need it for GitHub secrets!

## If Service Principal Already Exists

If you see "Found an existing application instance", that's okay! The command will update it and still give you the credentials.

## Next Steps

1. Copy the JSON output
2. Go to GitHub → Settings → Secrets → Actions
3. Add secret: `AZURE_CREDENTIALS`
4. Paste the JSON
5. Save

## Quick Command (Copy-Paste Ready)

```bash
MSYS_NO_PATHCONV=1 az ad sp create-for-rbac --name "sentinel-github-actions" --role contributor --scopes "/subscriptions/caea5300-fef2-4d0e-b763-d1d328c33974/resourceGroups/sentinel-mlops-rg" --sdk-auth
```

