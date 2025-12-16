#!/bin/bash
# Complete GitHub Actions Setup Script
# This script helps you set up everything needed for GitHub Actions

set -e

# Load variables from .env if it exists
if [ -f .env ]; then
    source .env
fi

# Set defaults
RESOURCE_GROUP="${RESOURCE_GROUP:-sentinel-mlops-rg}"
SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-caea5300-fef2-4d0e-b763-d1d328c33974}"
WORKSPACE="${WORKSPACE_NAME:-sentinel-ml-workspace}"
SP_NAME="sentinel-github-actions"

echo "=========================================="
echo "GitHub Actions Setup for SentinelAI"
echo "=========================================="
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Subscription ID: $SUBSCRIPTION_ID"
echo "Workspace: $WORKSPACE"
echo ""

# Step 1: Check if service principal already exists
echo "Step 1: Checking for existing service principal..."
EXISTING_SP=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_SP" ] && [ "$EXISTING_SP" != "null" ]; then
    echo "⚠️  Service principal '$SP_NAME' already exists!"
    read -p "Do you want to create a new one or use existing? (new/existing) [existing]: " choice
    choice=${choice:-existing}
    
    if [ "$choice" = "new" ]; then
        echo "Deleting existing service principal..."
        az ad sp delete --id "$EXISTING_SP" 2>/dev/null || true
        CREATE_NEW=true
    else
        echo "Using existing service principal..."
        CREATE_NEW=false
    fi
else
    CREATE_NEW=true
fi

# Step 2: Create service principal
if [ "$CREATE_NEW" = true ]; then
    echo ""
    echo "Step 2: Creating service principal..."
    # Use MSYS_NO_PATHCONV=1 for Git Bash on Windows to prevent path conversion
    SP_OUTPUT=$(MSYS_NO_PATHCONV=1 az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role contributor \
        --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
        --sdk-auth)
    
    echo ""
    echo "=========================================="
    echo "✅ Service Principal Created!"
    echo "=========================================="
    echo ""
    echo "COPY THIS JSON TO GITHUB SECRETS:"
    echo "----------------------------------------"
    echo "$SP_OUTPUT"
    echo "----------------------------------------"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: AZURE_CREDENTIALS"
    echo "4. Value: Paste the JSON above"
    echo "5. Click 'Add secret'"
    echo ""
else
    echo ""
    echo "To get existing service principal credentials:"
    echo "az ad sp credential reset --name $SP_NAME --sdk-auth"
    echo ""
fi

# Step 3: Verify Azure resources
echo ""
echo "Step 3: Verifying Azure resources..."
echo "----------------------------------------"

check_resource() {
    local resource_type=$1
    local name=$2
    local version=$3
    
    if [ -n "$version" ]; then
        if az ml $resource_type show --name "$name" --version "$version" --query "name" -o tsv >/dev/null 2>&1; then
            echo "✅ $resource_type: $name (v$version)"
            return 0
        else
            echo "❌ $resource_type: $name (v$version) - NOT FOUND"
            return 1
        fi
    else
        if az ml $resource_type show --name "$name" --query "name" -o tsv >/dev/null 2>&1; then
            echo "✅ $resource_type: $name"
            return 0
        else
            echo "❌ $resource_type: $name - NOT FOUND"
            return 1
        fi
    fi
}

check_resource "workspace" "$WORKSPACE" ""
check_resource "compute" "cpu-cluster" ""
check_resource "data" "gun-dataset" "1"
check_resource "environment" "ultralytics-env" "2"

# Check AKS
if az aks show --name sentinel-aks --resource-group "$RESOURCE_GROUP" --query "name" -o tsv >/dev/null 2>&1; then
    echo "✅ AKS: sentinel-aks"
else
    echo "❌ AKS: sentinel-aks - NOT FOUND"
fi

echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""
echo "✅ Service principal: $SP_NAME"
echo "✅ Azure resources verified"
echo ""
echo "⚠️  IMPORTANT: Don't forget to add AZURE_CREDENTIALS to GitHub secrets!"
echo ""
echo "To test the workflow:"
echo "1. Add the secret to GitHub"
echo "2. Push to main branch or create a test PR"
echo "3. Watch the workflow run in Actions tab"
echo ""

