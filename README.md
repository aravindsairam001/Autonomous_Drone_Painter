# PX4 Autonomous Wall Spray Painting System

A comprehensive autonomous drone spray painting system for PX4 Autopilot using MAVSDK Python. This system enables drones to perform precise wall painting missions with customizable wall dimensions, automated drone positioning, and intelligent spray patterns.

## 🎯 Overview

This project provides three main scripts that work together to create a complete autonomous wall spray painting solution:

1. **`interactive_wall_generator.py`** - Generate custom walls with user-defined dimensions
2. **`update_drone_spawn_pose.py`** - Calculate optimal drone spawn positions relative to wall
3. **`wall_spray_painting_advanced.py`** - Execute autonomous spray painting missions with advanced patterns

## 🏗️ System Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────────┐
│ Interactive Wall    │───▶│ Drone Spawn Position │───▶│ Advanced Spray Painting │
│ Generator           │    │ Calculator           │    │ Mission Executor        │
│                     │    │                      │    │                         │
│ • Custom dimensions │    │ • Optimal positioning│    │ • Vertical patterns     │
│ • Gazebo world gen  │    │ • Safety margins     │    │ • Horizontal patterns   │
│ • JSON config       │    │ • Launch script      │    │ • Speed control         │
└─────────────────────┘    └──────────────────────┘    └─────────────────────────┘
```

## 📁 Project Structure

```
Autonomous_Drone_Painter/
├── interactive_wall_generator.py      # Wall world generation script
├── update_drone_spawn_pose.py         # Drone positioning calculator
├── wall_spray_painting_advanced.py    # Main spray painting mission
├── requirements.txt                   # Core Python dependencies
├── requirements-dev.txt               # Development dependencies
├── setup.py                          # Package configuration
├── install.sh                        # Automated installation script
├── Makefile                          # Development automation
├── .gitignore                        # Git exclusions
├── README.md                         # This documentation
└── worlds/                           # Generated world files (created by scripts)
    └── paint_wall/
        ├── paint_wall.world          # Gazebo world file
        ├── paint_wall_config.json    # Wall configuration
        └── launch_with_spawn.sh      # Launch script
```

horizontal_paint-VEED.gif

## 📦 Dependencies

### Core Requirements
- **Python 3.7+** - Base language requirement
- **MAVSDK Python ≥1.4.0** - Main drone communication library
- **Built-in modules**: asyncio, json, math, xml.etree.ElementTree, os, sys, argparse, datetime

### Optional Dependencies
- **numpy ≥1.20.0** - For advanced numerical computations
- **matplotlib ≥3.3.0** - For mission visualization and plotting

### Development Dependencies
- **pytest ≥6.0.0** - Testing framework
- **black ≥21.0.0** - Code formatting
- **flake8 ≥3.9.0** - Code linting
- **mypy ≥0.910** - Type checking
- **sphinx ≥4.0.0** - Documentation generation

## 📋 Prerequisites

### Required Software
- **PX4 Autopilot** (latest stable version)
- **Gazebo Classic** (for simulation)
- **Python 3.7+**
- **MAVSDK Python** (`pip install mavsdk`)

### PX4 Autopilot Setup
1. Clone the PX4 Autopilot repository:
   ```bash
   git clone https://github.com/PX4/PX4-Autopilot.git
   cd PX4-Autopilot
   ```

2. Build PX4 for SITL simulation:
   ```bash
   make px4_sitl_default gazebo-classic
   ```

## 🚀 Installation

### Quick Start (Automated)
```bash
# Clone this repository
git clone https://github.com/aravindsairam001/Autonomous_Drone_Painter.git
cd Autonomous_Drone_Painter

# Run automated installation
./install.sh                    # Basic installation
./install.sh --venv            # Install in virtual environment  
./install.sh --dev             # Install with development dependencies
```

### Manual Installation

#### Step 1: Clone PX4 Autopilot (if not done already)
```bash
git clone https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
```

#### Step 2: Install Required Python Dependencies

**Option A: Using requirements.txt (Recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Manual installation**
```bash
pip install mavsdk>=1.4.0
# Note: asyncio, json, math, xml.etree.ElementTree, os, sys are built-in Python modules
```

**Option C: Install with development dependencies**
```bash
pip install -r requirements-dev.txt
```

**Option D: Install as a package**
```bash
pip install -e .              # Development mode
# or
pip install .                 # Regular installation
```

#### Step 3: Place Scripts in PX4 Directory
Copy the three provided scripts to the PX4 Tools directory:
```bash
# Place these files in PX4-Autopilot/Tools/
cp *.py /path/to/PX4-Autopilot/Tools/
```

#### Step 4: Set Executable Permissions
```bash
cd PX4-Autopilot/Tools
chmod +x interactive_wall_generator.py
chmod +x update_drone_spawn_pose.py
chmod +x wall_spray_painting_advanced.py
```

### Alternative: Using Makefile
```bash
make install                   # Basic installation
make install-dev              # With development dependencies
make install-venv             # In virtual environment
make px4-setup                # Show PX4 setup instructions
```

## 📝 Usage Guide

### 1. Generate Custom Wall (`interactive_wall_generator.py`)

This script creates a custom wall with user-defined dimensions and generates all necessary files for simulation.

```bash
cd PX4-Autopilot/Tools
python3 interactive_wall_generator.py
```

**Interactive Prompts:**
- Wall width (meters) - e.g., `15.0`
- Wall height (meters) - e.g., `5.0`  
- Wall thickness (meters) - e.g., `0.2`
- Wall position X (meters) - e.g., `7.0`
- Wall position Y (meters) - e.g., `0.0`

**Generated Files:**
- `worlds/paint_wall/paint_wall.world` - Gazebo world file
- `worlds/paint_wall/paint_wall_config.json` - Wall configuration
- `launch/paint_wall_launch.sh` - Launch script

### 2. Calculate Drone Spawn Position (`update_drone_spawn_pose.py`)

This script automatically calculates the optimal drone spawn position based on wall configuration.

```bash
python3 update_drone_spawn_pose.py
```

**What it does:**
- Reads wall configuration from JSON
- Calculates optimal drone position (left edge of wall, 1.5m distance)
- Generates launch script with correct spawn coordinates
- Updates environment variables for PX4 SITL

**Output:**
- `launch_with_spawn.sh` - Updated launch script with drone spawn position

### 3. Execute Spray Painting Mission (`wall_spray_painting_advanced.py`)

This script performs the autonomous spray painting mission with advanced pattern selection.

```bash
python3 wall_spray_painting_advanced.py
```

**Features:**
- **Pattern Selection**: Choose between vertical or horizontal rectangular patterns
- **Speed Control**: Configurable speeds for different movement types
- **Safety Features**: Return to takeoff position, emergency handling
- **Real-time Feedback**: Detailed mission progress and status updates

**Pattern Types:**
- **Vertical Pattern**: Paint up/down first, then move sideways (38 stripes for 15m wall)
- **Horizontal Pattern**: Paint left/right first, then move up/down (13 stripes for 5m wall)

## 🎮 Complete Workflow

### Step-by-Step Mission Execution

1. **Generate Wall:**
   ```bash
   python3 interactive_wall_generator.py
   # Follow prompts to create custom wall
   ```

2. **Calculate Drone Position:**
   ```bash
   python3 update_drone_spawn_pose.py
   # Generates optimal spawn coordinates
   ```

3. **Start PX4 SITL Simulation:**
   ```bash
   # Terminal 1: Start PX4 SITL with custom world
   ./launch_with_spawn.sh
   ```

4. **Execute Spray Painting Mission:**
   ```bash
   # Terminal 2: Run spray painting mission
   python3 wall_spray_painting_advanced.py
   # Select pattern type (1=Vertical, 2=Horizontal)
   ```

### Alternative: Using Makefile Commands
```bash
make run-wall-generator        # Generate custom wall
make run-spawn-updater         # Calculate drone position  
make run-painter              # Execute spray painting mission
make full-workflow            # Complete setup workflow
```

### Alternative: Using Package Entry Points
If installed as a package (`pip install -e .`):
```bash
wall-generator                # Interactive wall generator
drone-spawn-updater          # Drone spawn position calculator
wall-painter                 # Spray painting mission executor
```

## 🛠️ Development

### Development Setup
```bash
# Install with development dependencies
pip install -r requirements-dev.txt

# Or use Make
make install-dev
make dev-setup               # Includes pre-commit hooks
```

### Code Quality
```bash
make format                  # Format code with black
make lint                    # Run linting with flake8  
make type-check             # Run type checking with mypy
make test                   # Run tests with pytest
make dev-check              # Run all quality checks
```

### Testing
```bash
pytest tests/ -v --cov=. --cov-report=html --cov-report=term
```

### Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv px4_painter_env
source px4_painter_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## 🔧 Technical Details

### Coordinate System (NED)
- **North (X)**: Forward/backward relative to drone spawn
- **East (Y)**: Left/right relative to drone spawn  
- **Down (Z)**: Altitude (negative = above ground)

### Waypoint Calculation Logic

**Vertical Pattern:**
- Divides wall width into 0.4m stripes
- 3-phase movement per stripe: UP → HORIZONTAL → DOWN
- Alternates direction for efficiency

**Horizontal Pattern:**
- Divides wall height into 0.4m stripes  
- 2-phase movement per stripe: UP → HORIZONTAL
- Alternates left/right direction

### Speed Configuration
- **Vertical Speed**: 0.8-1.2 m/s (up/down movements)
- **Horizontal Speed**: 0.8-1.2 m/s (sideways movements)
- **Positioning Speed**: 1.5 m/s (navigation between waypoints)

## 📊 Example Configuration

### Wall Specifications
```json
{
  "main_wall": {
    "dimensions": {
      "width": 15.0,
      "height": 5.0,
      "thickness": 0.2
    },
    "position": {
      "x": 7.0,
      "y": 0.0,
      "z": 2.5
    }
  }
}
```

### Drone Spawn Position
```bash
# Calculated automatically based on wall config
PX4_SPAWN_X=-0.50  # Left edge of wall
PX4_SPAWN_Y=-1.60  # 1.5m in front of wall  
PX4_SPAWN_Z=1.00   # 1m above ground
PX4_SPAWN_YAW=0.0  # Facing wall
```

## 🛡️ Safety Features

- **Return to Home**: Drone returns to takeoff position after mission
- **Emergency Handling**: Safe landing procedures for mission failures
- **Boundary Checking**: Prevents waypoints outside wall dimensions
- **Speed Limits**: Configurable speed limits for safe operation
- **Timeout Protection**: Maximum time limits for waypoint navigation

## 🐛 Troubleshooting

### Common Issues

**1. MAVSDK Connection Failed**
```bash
# Ensure PX4 SITL is running first
./launch_with_spawn.sh
# Then run spray painting script in separate terminal
```

**2. Wall Configuration Not Found**
```bash
# Run wall generator first
python3 interactive_wall_generator.py
```

**3. Drone Spawn Position Incorrect**
```bash
# Recalculate spawn position
python3 update_drone_spawn_pose.py
```

**4. Offboard Mode Timeout**
```bash
# This is normal during landing - script handles it automatically
# Check final drone status for confirmation
```

**5. Dependencies Installation Issues**
```bash
# Make sure you have the right Python version
python3 --version  # Should be 3.7+

# Use the automated installer
./install.sh --venv

# Or install step by step
pip install --upgrade pip
pip install -r requirements.txt
```

**6. Permission Denied on Scripts**
```bash
# Make scripts executable
chmod +x *.py
chmod +x install.sh
```

**7. Missing Virtual Environment**
```bash
# Create virtual environment
python3 -m venv px4_painter_env
source px4_painter_env/bin/activate
pip install -r requirements.txt
```

## 📈 Performance Metrics

- **Coverage Efficiency**: 100% wall surface coverage
- **Mission Time**: ~5-8 minutes for 15m×5m wall
- **Waypoint Accuracy**: ±0.3m tolerance
- **Pattern Completion**: 38 stripes (vertical) or 26 waypoints (horizontal)

## 🔮 Future Enhancements

- Integration with real spray painting hardware
- Dynamic obstacle avoidance
- Multi-wall mission planning
- Weather condition adaptation
- Real-time paint level monitoring

## 📋 File Descriptions

### Core Scripts
- **`interactive_wall_generator.py`** - Interactive wall world generator with customizable dimensions
- **`update_drone_spawn_pose.py`** - Calculates optimal drone spawn positions relative to walls
- **`wall_spray_painting_advanced.py`** - Main autonomous spray painting mission executor

### Configuration Files
- **`requirements.txt`** - Core Python dependencies (MAVSDK, numpy, matplotlib)
- **`requirements-dev.txt`** - Development dependencies (testing, linting, documentation)
- **`setup.py`** - Python package configuration with entry points
- **`.gitignore`** - Git version control exclusions

### Automation & Development
- **`install.sh`** - Automated installation script with virtual environment support
- **`Makefile`** - Development automation (install, test, format, lint, run tasks)

### Generated Files (Created by Scripts)
- **`worlds/paint_wall/paint_wall.world`** - Gazebo Classic world file
- **`worlds/paint_wall/paint_wall_config.json`** - Wall configuration data
- **`worlds/paint_wall/launch_with_spawn.sh`** - PX4 SITL launch script

## 📞 Support

For issues related to:
- **PX4 Autopilot**: [PX4 Documentation](https://docs.px4.io/)
- **MAVSDK Python**: [MAVSDK Documentation](https://mavsdk.mavlink.io/main/en/)
- **Gazebo Classic**: [Gazebo Documentation](http://gazebosim.org/tutorials)

## 📄 License

This project is designed to work with PX4 Autopilot and follows the same BSD 3-Clause License.

---

**Author**: aravindsairam001  
**GitHub**: https://github.com/aravindsairam001/Autonomous_Drone_Painter  
**Version**: 1.0  
**Last Updated**: August 2025  

> **Note**: This system is designed for simulation and educational purposes. For real-world implementation, additional safety measures and hardware integration are required.
