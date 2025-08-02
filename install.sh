#!/bin/bash
# 
# PX4 Autonomous Wall Spray Painting System - Installation Script
# This script sets up the complete environment for the drone spray painting system
#

set -e  # Exit on any error

echo "🚀 PX4 Autonomous Wall Spray Painting System - Installation"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.7"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_status "Python $python_version is compatible (>= 3.7 required)"
else
    print_error "Python 3.7+ is required. Current version: $python_version"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

print_status "pip3 is available"

# Create virtual environment if requested
if [[ "$1" == "--venv" ]]; then
    print_info "Creating virtual environment..."
    python3 -m venv px4_painter_env
    source px4_painter_env/bin/activate
    print_status "Virtual environment created and activated"
fi

# Upgrade pip
print_info "Upgrading pip..."
pip3 install --upgrade pip

# Install requirements
print_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_status "Core requirements installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Install development dependencies if flag is provided
if [[ "$*" == *"--dev"* ]]; then
    print_info "Installing development dependencies..."
    if [ -f "requirements-dev.txt" ]; then
        pip3 install -r requirements-dev.txt
        print_status "Development dependencies installed"
    else
        print_warning "requirements-dev.txt not found, skipping dev dependencies"
    fi
fi

# Install the package in development mode
print_info "Installing package in development mode..."
pip3 install -e .
print_status "Package installed in development mode"

# Check MAVSDK installation
print_info "Verifying MAVSDK installation..."
if python3 -c "import mavsdk; print(f'MAVSDK version: {mavsdk.__version__}')" 2>/dev/null; then
    print_status "MAVSDK Python is properly installed"
else
    print_error "MAVSDK Python installation failed!"
    exit 1
fi

# Make scripts executable
print_info "Setting executable permissions on scripts..."
chmod +x interactive_wall_generator.py
chmod +x update_drone_spawn_pose.py  
chmod +x wall_spray_painting_advanced.py
print_status "Scripts are now executable"

# Check for PX4 Autopilot
print_info "Checking for PX4 Autopilot..."
if [ -d "../PX4-Autopilot" ] || [ -d "../../PX4-Autopilot" ] || [ -d "/opt/PX4-Autopilot" ]; then
    print_status "PX4 Autopilot directory found"
else
    print_warning "PX4 Autopilot not found in common locations"
    print_info "You may need to clone PX4 Autopilot:"
    echo "  git clone https://github.com/PX4/PX4-Autopilot.git"
    echo "  cd PX4-Autopilot"
    echo "  make px4_sitl_default gazebo-classic"
fi

# Display next steps
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
print_info "Next steps:"
echo "1. If you don't have PX4 Autopilot, clone and build it:"
echo "   git clone https://github.com/PX4/PX4-Autopilot.git"
echo "   cd PX4-Autopilot"
echo "   make px4_sitl_default gazebo-classic"
echo ""
echo "2. Copy the scripts to PX4-Autopilot/Tools/:"
echo "   cp *.py /path/to/PX4-Autopilot/Tools/"
echo ""
echo "3. Run the wall generator:"
echo "   python3 interactive_wall_generator.py"
echo ""
echo "4. Update drone spawn position:"
echo "   python3 update_drone_spawn_pose.py"
echo ""
echo "5. Start PX4 SITL and run the spray painting mission:"
echo "   ./launch_with_spawn.sh"
echo "   python3 wall_spray_painting_advanced.py"
echo ""

if [[ "$1" == "--venv" ]]; then
    print_info "To activate the virtual environment in the future:"
    echo "   source px4_painter_env/bin/activate"
fi

print_status "Installation completed successfully!"
