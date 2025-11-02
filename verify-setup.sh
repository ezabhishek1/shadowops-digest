#!/bin/bash

# ShadowOps Digest - Setup Verification Script
# This script checks if your environment is ready to run the application

echo "🔍 ShadowOps Digest - Setup Verification"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        if [ ! -z "$2" ]; then
            version=$($1 $2 2>&1)
            echo "  Version: $version"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        return 1
    fi
}

check_env_var() {
    if [ ! -z "${!1}" ]; then
        echo -e "${GREEN}✓${NC} $1 is set"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $1 is not set"
        return 1
    fi
}

# Track overall status
all_good=true

# Check prerequisites
echo "📋 Checking Prerequisites..."
echo ""

check_command "python" "--version" || check_command "python3" "--version" || all_good=false
check_command "pip" "--version" || check_command "pip3" "--version" || all_good=false
check_command "node" "--version" || all_good=false
check_command "npm" "--version" || all_good=false
check_command "git" "--version" || all_good=false

echo ""
echo "🐳 Checking Docker (Optional)..."
echo ""
check_command "docker" "--version"
check_command "docker-compose" "--version" || check_command "docker" "compose version"

echo ""
echo "📁 Checking Project Files..."
echo ""

check_file ".env.example" || all_good=false
check_file "backend/requirements.txt" || all_good=false
check_file "backend/main.py" || all_good=false
check_file "frontend/package.json" || all_good=false
check_file "docker-compose.yml" || all_good=false

echo ""
echo "🔑 Checking Environment Variables..."
echo ""

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    source .env 2>/dev/null
    check_env_var "OPENAI_API_KEY"
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "  Run: cp .env.example .env"
    all_good=false
fi

echo ""
echo "🔌 Checking Ports..."
echo ""

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep ":$1 " | grep LISTEN >/dev/null; then
        echo -e "${YELLOW}⚠${NC} Port $1 is in use"
        return 1
    else
        echo -e "${GREEN}✓${NC} Port $1 is available"
        return 0
    fi
}

check_port 3000
check_port 8000
check_port 5432

echo ""
echo "========================================"
echo ""

if [ "$all_good" = true ]; then
    echo -e "${GREEN}✅ All checks passed! You're ready to run ShadowOps Digest.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Make sure .env has your OpenAI API key"
    echo "  2. Run: docker-compose up --build"
    echo "  3. Or see QUICKSTART.md for local setup"
else
    echo -e "${RED}❌ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "Need help? Check:"
    echo "  - README.md for detailed setup instructions"
    echo "  - QUICKSTART.md for quick start guide"
    echo "  - docs/DEPLOYMENT.md for troubleshooting"
fi

echo ""
