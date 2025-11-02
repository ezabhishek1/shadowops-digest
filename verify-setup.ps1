# ShadowOps Digest - Setup Verification Script (PowerShell)
# This script checks if your environment is ready to run the application

Write-Host "🔍 ShadowOps Digest - Setup Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check if command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Python
if (Test-Command "python") {
    Write-Host "✓ Python is installed" -ForegroundColor Green
    $pythonVersion = python --version
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host "✗ Python is NOT installed" -ForegroundColor Red
    $allGood = $false
}

# Pip
if (Test-Command "pip") {
    Write-Host "✓ pip is installed" -ForegroundColor Green
    $pipVersion = pip --version
    Write-Host "  Version: $pipVersion" -ForegroundColor Gray
} else {
    Write-Host "✗ pip is NOT installed" -ForegroundColor Red
    $allGood = $false
}

# Node
if (Test-Command "node") {
    Write-Host "✓ Node.js is installed" -ForegroundColor Green
    $nodeVersion = node --version
    Write-Host "  Version: $nodeVersion" -ForegroundColor Gray
} else {
    Write-Host "✗ Node.js is NOT installed" -ForegroundColor Red
    $allGood = $false
}

# npm
if (Test-Command "npm") {
    Write-Host "✓ npm is installed" -ForegroundColor Green
    $npmVersion = npm --version
    Write-Host "  Version: $npmVersion" -ForegroundColor Gray
} else {
    Write-Host "✗ npm is NOT installed" -ForegroundColor Red
    $allGood = $false
}

# Git
if (Test-Command "git") {
    Write-Host "✓ Git is installed" -ForegroundColor Green
    $gitVersion = git --version
    Write-Host "  Version: $gitVersion" -ForegroundColor Gray
} else {
    Write-Host "✗ Git is NOT installed" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "🐳 Checking Docker (Optional)..." -ForegroundColor Yellow
Write-Host ""

if (Test-Command "docker") {
    Write-Host "✓ Docker is installed" -ForegroundColor Green
    $dockerVersion = docker --version
    Write-Host "  Version: $dockerVersion" -ForegroundColor Gray
} else {
    Write-Host "⚠ Docker is not installed (optional)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📁 Checking Project Files..." -ForegroundColor Yellow
Write-Host ""

$files = @(
    ".env.example",
    "backend\requirements.txt",
    "backend\main.py",
    "frontend\package.json",
    "docker-compose.yml"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file is missing" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "🔑 Checking Environment Variables..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
    
    # Check for OPENAI_API_KEY
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=.+") {
        Write-Host "✓ OPENAI_API_KEY is set in .env" -ForegroundColor Green
    } else {
        Write-Host "⚠ OPENAI_API_KEY is not set in .env" -ForegroundColor Yellow
        Write-Host "  Add your OpenAI API key to .env file" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "  Run: cp .env.example .env" -ForegroundColor Gray
    $allGood = $false
}

Write-Host ""
Write-Host "🔌 Checking Ports..." -ForegroundColor Yellow
Write-Host ""

$ports = @(3000, 8000, 5432)

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠ Port $port is in use" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Port $port is available" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "✅ All checks passed! You're ready to run ShadowOps Digest." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Make sure .env has your OpenAI API key"
    Write-Host "  2. Run: docker-compose up --build"
    Write-Host "  3. Or see QUICKSTART.md for local setup"
} else {
    Write-Host "❌ Some checks failed. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Need help? Check:" -ForegroundColor Cyan
    Write-Host "  - README.md for detailed setup instructions"
    Write-Host "  - QUICKSTART.md for quick start guide"
    Write-Host "  - docs/DEPLOYMENT.md for troubleshooting"
}

Write-Host ""
