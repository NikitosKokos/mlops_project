@echo off
REM GitHub Actions Setup Script for Windows
REM This script helps you set up everything needed for GitHub Actions

setlocal enabledelayedexpansion

REM Load variables from .env if it exists
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
)

REM Set defaults
if not defined RESOURCE_GROUP set RESOURCE_GROUP=sentinel-mlops-rg
if not defined SUBSCRIPTION_ID set SUBSCRIPTION_ID=caea5300-fef2-4d0e-b763-d1d328c33974
if not defined WORKSPACE_NAME set WORKSPACE_NAME=sentinel-ml-workspace
set SP_NAME=sentinel-github-actions

echo ==========================================
echo GitHub Actions Setup for SentinelAI
echo ==========================================
echo.
echo Resource Group: %RESOURCE_GROUP%
echo Subscription ID: %SUBSCRIPTION_ID%
echo Workspace: %WORKSPACE_NAME%
echo.

REM Step 1: Check if service principal already exists
echo Step 1: Checking for existing service principal...
az ad sp list --display-name "%SP_NAME%" --query "[0].appId" -o tsv > temp_sp.txt 2>nul
set /p EXISTING_SP=<temp_sp.txt
del temp_sp.txt

if not "%EXISTING_SP%"=="" if not "%EXISTING_SP%"=="null" (
    echo ⚠️  Service principal '%SP_NAME%' already exists!
    set /p choice="Do you want to create a new one or use existing? (new/existing) [existing]: "
    if "!choice!"=="" set choice=existing
    if "!choice!"=="new" (
        echo Deleting existing service principal...
        az ad sp delete --id "%EXISTING_SP%" 2>nul
        set CREATE_NEW=true
    ) else (
        echo Using existing service principal...
        set CREATE_NEW=false
    )
) else (
    set CREATE_NEW=true
)

REM Step 2: Create service principal
if "%CREATE_NEW%"=="true" (
    echo.
    echo Step 2: Creating service principal...
    echo Note: If using Git Bash, use: MSYS_NO_PATHCONV=1 az ad sp create-for-rbac ...
    az ad sp create-for-rbac --name "%SP_NAME%" --role contributor --scopes "/subscriptions/%SUBSCRIPTION_ID%/resourceGroups/%RESOURCE_GROUP%" --sdk-auth > sp_output.json
    
    echo.
    echo ==========================================
    echo ✅ Service Principal Created!
    echo ==========================================
    echo.
    echo COPY THIS JSON TO GITHUB SECRETS:
    echo ----------------------------------------
    type sp_output.json
    echo ----------------------------------------
    echo.
    echo Next steps:
    echo 1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
    echo 2. Click 'New repository secret'
    echo 3. Name: AZURE_CREDENTIALS
    echo 4. Value: Paste the JSON above
    echo 5. Click 'Add secret'
    echo.
    echo JSON saved to: sp_output.json
) else (
    echo.
    echo To get existing service principal credentials:
    echo az ad sp credential reset --name %SP_NAME% --sdk-auth
)

REM Step 3: Verify Azure resources
echo.
echo Step 3: Verifying Azure resources...
echo ----------------------------------------

az ml workspace show --name "%WORKSPACE_NAME%" --resource-group "%RESOURCE_GROUP%" --query "name" -o tsv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Workspace: %WORKSPACE_NAME%
) else (
    echo ❌ Workspace: %WORKSPACE_NAME% - NOT FOUND
)

az ml compute show --name cpu-cluster --query "name" -o tsv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Compute: cpu-cluster
) else (
    echo ❌ Compute: cpu-cluster - NOT FOUND
)

az ml data show --name gun-dataset --version 1 --query "name" -o tsv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Dataset: gun-dataset ^(v1^)
) else (
    echo ❌ Dataset: gun-dataset ^(v1^) - NOT FOUND
)

az ml environment show --name ultralytics-env --version 2 --query "name" -o tsv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Environment: ultralytics-env ^(v2^)
) else (
    echo ❌ Environment: ultralytics-env ^(v2^) - NOT FOUND
)

az aks show --name sentinel-aks --resource-group "%RESOURCE_GROUP%" --query "name" -o tsv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ AKS: sentinel-aks
) else (
    echo ❌ AKS: sentinel-aks - NOT FOUND
)

echo.
echo ==========================================
echo Setup Summary
echo ==========================================
echo.
echo ✅ Service principal: %SP_NAME%
echo ✅ Azure resources verified
echo.
echo ⚠️  IMPORTANT: Don't forget to add AZURE_CREDENTIALS to GitHub secrets!
echo.
echo To test the workflow:
echo 1. Add the secret to GitHub
echo 2. Push to main branch or create a test PR
echo 3. Watch the workflow run in Actions tab
echo.

endlocal

