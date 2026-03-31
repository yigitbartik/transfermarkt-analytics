#!/bin/bash

# =========================================
# Transfermarkt Analytics Pro - macOS/Linux
# =========================================
# This script automatically:
#   1. Checks Python installation
#   2. Creates virtual environment
#   3. Installs dependencies
#   4. Launches the Streamlit app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Helper functions
print_header() {
    clear
    echo ""
    echo "========================================="
    echo "  Transfermarkt Analytics Pro v2.0"
    echo "  macOS/Linux Startup Script"
    echo "========================================="
    echo ""
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo ""
        echo "Please install Python 3.9+ from:"
        echo "  https://www.python.org/"
        echo ""
        echo "Or using package manager:"
        echo "  macOS: brew install python@3.11"
        echo "  Ubuntu/Debian: sudo apt-get install python3.11"
        echo "  Fedora/RHEL: sudo dnf install python3.11"
        echo ""
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_ok "Python $PYTHON_VERSION found"
}

# Function to check Python version
check_python_version() {
    MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        print_error "Python 3.9+ is required"
        echo "You have: Python $MAJOR.$MINOR"
        exit 1
    fi
}

# Function to create and activate venv
setup_venv() {
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv 2>/dev/null || {
            print_error "Failed to create virtual environment"
            echo ""
            echo "Possible solutions:"
            echo "  - Check you have write permissions"
            echo "  - Ensure enough disk space is available"
            echo "  - Try: sudo apt-get install python3.11-venv (Linux)"
            echo ""
            exit 1
        }
        print_ok "Virtual environment created"
    else
        print_ok "Virtual environment found"
    fi
    
    print_info "Activating virtual environment..."
    source venv/bin/activate
}

# Function to install dependencies
install_dependencies() {
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Installing dependencies (may take 2-3 minutes)..."
    echo ""
    
    # Upgrade pip first
    python -m pip install --upgrade pip setuptools wheel -q
    
    # Install requirements
    pip install -r requirements.txt 2>&1 | grep -E "(Successfully|Collecting|Installing)" || true
    
    echo ""
    print_ok "Dependencies installed successfully"
}

# Function to check port availability
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to find available port
find_available_port() {
    local port=8501
    while check_port $port; do
        port=$((port + 1))
        if [ $port -gt 8510 ]; then
            print_error "Could not find an available port"
            exit 1
        fi
    done
    echo $port
}

# Main execution
main() {
    print_header
    
    # Step 1: Check Python
    print_info "Checking Python installation..."
    check_python
    check_python_version
    echo ""
    
    # Step 2: Setup virtual environment
    print_info "Setting up virtual environment..."
    setup_venv
    echo ""
    
    # Step 3: Install dependencies
    if [ ! -d "venv/lib/python3.*/site-packages/streamlit" ]; then
        install_dependencies
        echo ""
    else
        print_ok "Dependencies already installed"
        echo ""
    fi
    
    # Step 4: Launch application
    print_info "Launching Streamlit application..."
    echo ""
    echo "========================================="
    echo "  Starting Application"
    echo "========================================="
    echo ""
    
    PORT=$(find_available_port)
    
    if [ $PORT -eq 8501 ]; then
        print_ok "Opening at: http://localhost:8501"
    else
        print_warning "Port 8501 is in use, using port $PORT instead"
        print_ok "Opening at: http://localhost:$PORT"
    fi
    
    echo ""
    print_info "Press Ctrl+C to stop the server"
    print_info "First load may take 30 seconds..."
    echo ""
    
    # Run Streamlit
    if [ $PORT -eq 8501 ]; then
        streamlit run app.py
    else
        streamlit run app.py --server.port $PORT
    fi
}

# Run main function
main
exit 0
