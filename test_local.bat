@echo off
REM Quick local testing script for SentinelAI (Windows)
REM Usage: test_local.bat [image_path]

set API_URL=http://localhost:8000
set IMAGE_PATH=%1

echo ==========================================
echo SentinelAI Local Testing Script
echo ==========================================
echo.

REM Check if API is running
echo Checking if API is running...
curl -s -f "%API_URL%/" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API is running at %API_URL%
) else (
    echo ❌ API is not running!
    echo    Start it with: cd inference ^&^& uvicorn main:app --reload
    exit /b 1
)

REM Test health endpoint
echo.
echo Testing health endpoint...
python inference\test_api.py --health "%API_URL%"
if %errorlevel% neq 0 exit /b %errorlevel%

REM Test detection if image provided
if not "%IMAGE_PATH%"=="" (
    echo.
    echo Testing detection endpoint...
    if exist "%IMAGE_PATH%" (
        python inference\test_api.py "%IMAGE_PATH%" "%API_URL%"
        if %errorlevel% neq 0 exit /b %errorlevel%
    ) else (
        echo ❌ Image file not found: %IMAGE_PATH%
        exit /b 1
    )
) else (
    echo.
    echo ⚠️  No image provided. Skipping detection test.
    echo    Usage: test_local.bat ^<image_path^>
)

echo.
echo ==========================================
echo Testing complete!
echo ==========================================

