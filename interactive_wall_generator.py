#!/usr/bin/env python3
"""
Interactive Wall World Generator for PX4 Gazebo Classic Simulation
Takes user inputs for wall dimensions and generates simulation files
"""

import argparse
import os
import sys
import json
from datetime import datetime

class WallWorldGenerator:
    def __init__(self):
        self.world_name = None
        self.wall_config = {}
        self.output_dir = None

    def get_user_inputs(self):
        """Interactive function to get wall configuration from user"""
        print("🏗️  PX4 Gazebo Classic Wall World Generator")
        print("=" * 50)
        print("Let's create a custom wall world for your drone simulation!\n")

        # World name
        while True:
            world_name = input("Enter world name (default: 'custom_wall'): ").strip()
            if not world_name:
                world_name = "custom_wall"

            # Validate world name (alphanumeric and underscores only)
            if world_name.replace('_', '').replace('-', '').isalnum():
                self.world_name = world_name
                break
            else:
                print("❌ World name should contain only letters, numbers, hyphens, and underscores")

        print(f"✅ World name: {self.world_name}\n")

        # Wall dimensions
        print("📏 Wall Dimensions:")
        self.wall_config['width'] = self.get_float_input("Wall width (meters)", 5.0, 0.1, 50.0)
        self.wall_config['height'] = self.get_float_input("Wall height (meters)", 3.0, 0.1, 20.0)
        self.wall_config['thickness'] = self.get_float_input("Wall thickness (meters)", 0.2, 0.05, 2.0)

        print("\n📍 Wall Position:")
        self.wall_config['x'] = self.get_float_input("Wall X position (meters from origin)", 5.0, -50.0, 50.0)
        self.wall_config['y'] = self.get_float_input("Wall Y position (meters from origin)", 0.0, -50.0, 50.0)

        print("\n🎨 Wall Appearance:")
        color_options = {
            '1': ('White', (0.9, 0.9, 0.9, 1.0)),
            '2': ('Gray', (0.5, 0.5, 0.5, 1.0)),
            '3': ('Red', (0.8, 0.2, 0.2, 1.0)),
            '4': ('Blue', (0.2, 0.2, 0.8, 1.0)),
            '5': ('Green', (0.2, 0.8, 0.2, 1.0)),
            '6': ('Yellow', (0.9, 0.9, 0.2, 1.0))
        }

        print("Choose wall color:")
        for key, (name, _) in color_options.items():
            print(f"  {key}. {name}")

        while True:
            color_choice = input("Enter color choice (1-6, default: 1): ").strip()
            if not color_choice:
                color_choice = '1'

            if color_choice in color_options:
                color_name, color_rgba = color_options[color_choice]
                self.wall_config['color_name'] = color_name
                self.wall_config['color'] = color_rgba
                break
            else:
                print("❌ Please enter a number between 1 and 6")

        print(f"✅ Wall color: {self.wall_config['color_name']}\n")

        # Multiple walls option
        print("🔢 Multiple Walls:")
        add_more = input("Add more walls? (y/N): ").strip().lower()

        self.wall_config['additional_walls'] = []
        if add_more in ['y', 'yes']:
            wall_count = self.get_int_input("How many additional walls?", 1, 1, 10)

            for i in range(wall_count):
                print(f"\n--- Additional Wall {i+1} ---")
                wall = {}
                wall['width'] = self.get_float_input(f"Wall {i+1} width (meters)", 3.0, 0.1, 50.0)
                wall['height'] = self.get_float_input(f"Wall {i+1} height (meters)", 2.0, 0.1, 20.0)
                wall['thickness'] = self.get_float_input(f"Wall {i+1} thickness (meters)", 0.2, 0.05, 2.0)
                wall['x'] = self.get_float_input(f"Wall {i+1} X position", 0.0, -50.0, 50.0)
                wall['y'] = self.get_float_input(f"Wall {i+1} Y position", 5.0, -50.0, 50.0)

                # Color for additional wall
                while True:
                    color_choice = input(f"Wall {i+1} color (1-6, default: 1): ").strip()
                    if not color_choice:
                        color_choice = '1'

                    if color_choice in color_options:
                        color_name, color_rgba = color_options[color_choice]
                        wall['color_name'] = color_name
                        wall['color'] = color_rgba
                        break
                    else:
                        print("❌ Please enter a number between 1 and 6")

                self.wall_config['additional_walls'].append(wall)

        # Output directory
        print("\n📁 Output Configuration:")
        default_output = f"worlds/{self.world_name}"
        output_dir = input(f"Output directory (default: '{default_output}'): ").strip()
        if not output_dir:
            output_dir = default_output

        self.output_dir = output_dir

        # Summary
        self.print_summary()

    def get_float_input(self, prompt, default, min_val, max_val):
        """Get and validate float input from user"""
        while True:
            try:
                value_str = input(f"{prompt} (default: {default}): ").strip()
                if not value_str:
                    return default

                value = float(value_str)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid number")

    def get_int_input(self, prompt, default, min_val, max_val):
        """Get and validate integer input from user"""
        while True:
            try:
                value_str = input(f"{prompt} (default: {default}): ").strip()
                if not value_str:
                    return default

                value = int(value_str)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"❌ Value must be between {min_val} and {max_val}")
            except ValueError:
                print("❌ Please enter a valid integer")

    def print_summary(self):
        """Print configuration summary"""
        print("\n" + "=" * 50)
        print("📋 CONFIGURATION SUMMARY")
        print("=" * 50)
        print(f"World Name: {self.world_name}")
        print(f"Output Directory: {self.output_dir}")
        print(f"\nMain Wall:")
        print(f"  Dimensions: {self.wall_config['width']}m × {self.wall_config['height']}m × {self.wall_config['thickness']}m")
        print(f"  Position: ({self.wall_config['x']}, {self.wall_config['y']})")
        print(f"  Color: {self.wall_config['color_name']}")

        if self.wall_config['additional_walls']:
            print(f"\nAdditional Walls: {len(self.wall_config['additional_walls'])}")
            for i, wall in enumerate(self.wall_config['additional_walls']):
                print(f"  Wall {i+1}: {wall['width']}×{wall['height']}×{wall['thickness']}m at ({wall['x']}, {wall['y']}) - {wall['color_name']}")

        print("=" * 50)

        confirm = input("\nGenerate files with this configuration? (Y/n): ").strip().lower()
        if confirm in ['n', 'no']:
            print("❌ Configuration cancelled. Exiting...")
            sys.exit(0)

    def create_wall_sdf(self, wall_config, wall_name="wall", wall_id=0):
        """Generate SDF for a single wall"""
        wall_z = wall_config['height'] / 2.0
        color = wall_config['color']

        return f'''    <!-- {wall_name.title()} -->
    <model name="{wall_name}_{wall_id}">
      <pose>{wall_config['x']} {wall_config['y']} {wall_z} 0 0 0</pose>
      <static>true</static>
      <link name="wall_link">
        <collision name="wall_collision">
          <geometry>
            <box>
              <size>{wall_config['width']} {wall_config['thickness']} {wall_config['height']}</size>
            </box>
          </geometry>
        </collision>
        <visual name="wall_visual">
          <geometry>
            <box>
              <size>{wall_config['width']} {wall_config['thickness']} {wall_config['height']}</size>
            </box>
          </geometry>
          <material>
            <ambient>{color[0]} {color[1]} {color[2]} {color[3]}</ambient>
            <diffuse>{color[0]} {color[1]} {color[2]} {color[3]}</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
    </model>
'''

    def generate_world_file(self):
        """Generate the complete world file for Gazebo Classic"""
        # Generate main wall
        walls_sdf = self.create_wall_sdf(self.wall_config, "main_wall", 0)

        # Generate additional walls
        for i, wall in enumerate(self.wall_config['additional_walls']):
            walls_sdf += self.create_wall_sdf(wall, "wall", i + 1)

        world_content = f'''<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="{self.world_name}_world">

    <!-- Physics Engine -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
      <ode>
        <solver>
          <type>quick</type>
          <iters>150</iters>
          <sor>1.400000</sor>
          <use_dynamic_moi_rescaling>1</use_dynamic_moi_rescaling>
        </solver>
        <constraints>
          <cfm>0.00001</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>2000.000000</contact_max_correcting_vel>
          <contact_surface_layer>0.01000</contact_surface_layer>
        </constraints>
      </ode>
    </physics>

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Scene Configuration -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 1 1</background>
      <shadows>true</shadows>
    </scene>

    <!-- Ground Plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.0 0.0 0.0 1</specular>
          </material>
        </visual>
      </link>
    </model>

{walls_sdf}
    <!-- Note: PX4 will spawn the iris drone automatically with proper sensors -->

  </world>
</sdf>'''
        return world_content

    def generate_launch_script(self):
        """Generate launch script for the custom world using Gazebo Classic"""
        script_content = f'''#!/bin/bash
#
# Launch PX4 SITL with {self.world_name} world using Gazebo Classic
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#

# Set the working directory to PX4-Autopilot root
cd "$(dirname "$0")/.."

# World configuration
WORLD_NAME="{self.world_name}"
WORLD_FILE="Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/${{WORLD_NAME}}.world"

# Check if world file exists
if [ ! -f "$WORLD_FILE" ]; then
    echo "❌ World file not found: $WORLD_FILE"
    echo "   Make sure you've copied the generated files to the PX4-Autopilot directory"
    echo "   For Gazebo Classic, copy to: Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/"
    exit 1
fi

echo "🚀 Launching PX4 SITL with ${{WORLD_NAME}} world..."
echo "   World: $WORLD_FILE"
echo "   Vehicle: iris quadcopter"
echo "   Simulator: Gazebo Classic"

# Set environment variables for PX4 SITL
export PX4_SIM_MODEL=iris
export PX4_SIMULATOR=gazebo-classic

# Launch PX4 SITL with iris in custom world
echo "Starting simulation..."
make px4_sitl gazebo-classic_${{WORLD_NAME}}

echo "✅ Launch complete!"
echo "   - PX4 SITL is running"
echo "   - Gazebo Classic world: ${{WORLD_NAME}}"
echo "   - Vehicle: iris at origin (0,0,0.1)"
echo ""
echo "📡 Connect QGroundControl to udp://localhost:18570"
'''
        return script_content

    def generate_config_file(self):
        """Generate JSON configuration file"""
        config = {
            "world_name": self.world_name,
            "generated_on": datetime.now().isoformat(),
            "simulator": "gazebo-classic",
            "vehicle": "iris",
            "main_wall": {
                "dimensions": {
                    "width": self.wall_config['width'],
                    "height": self.wall_config['height'],
                    "thickness": self.wall_config['thickness']
                },
                "position": {
                    "x": self.wall_config['x'],
                    "y": self.wall_config['y']
                },
                "color": {
                    "name": self.wall_config['color_name'],
                    "rgba": self.wall_config['color']
                }
            },
            "additional_walls": []
        }

        for i, wall in enumerate(self.wall_config['additional_walls']):
            config["additional_walls"].append({
                "id": i + 1,
                "dimensions": {
                    "width": wall['width'],
                    "height": wall['height'],
                    "thickness": wall['thickness']
                },
                "position": {
                    "x": wall['x'],
                    "y": wall['y']
                },
                "color": {
                    "name": wall['color_name'],
                    "rgba": wall['color']
                }
            })

        return json.dumps(config, indent=2)

    def generate_readme(self):
        """Generate README file with instructions"""
        total_walls = 1 + len(self.wall_config['additional_walls'])

        readme_content = f'''# {self.world_name.title()} World

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## World Description

This world contains {total_walls} wall(s) for drone simulation and testing using Gazebo Classic.

### Main Wall
- **Dimensions**: {self.wall_config['width']}m × {self.wall_config['height']}m × {self.wall_config['thickness']}m
- **Position**: ({self.wall_config['x']}, {self.wall_config['y']})
- **Color**: {self.wall_config['color_name']}
'''

        if self.wall_config['additional_walls']:
            readme_content += f"\n### Additional Walls\n"
            for i, wall in enumerate(self.wall_config['additional_walls']):
                readme_content += f"- **Wall {i+1}**: {wall['width']}×{wall['height']}×{wall['thickness']}m at ({wall['x']}, {wall['y']}) - {wall['color_name']}\n"

        readme_content += f'''
## Installation

1. Copy the generated files to your PX4-Autopilot directory:
   ```bash
   cp {self.world_name}.world /path/to/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/
   cp launch_{self.world_name}.sh /path/to/PX4-Autopilot/Tools/
   chmod +x /path/to/PX4-Autopilot/Tools/launch_{self.world_name}.sh
   ```

## Usage

### Method 1: Using the Launch Script
```bash
cd /path/to/PX4-Autopilot
./Tools/launch_{self.world_name}.sh
```

### Method 2: Direct Make Command
```bash
cd /path/to/PX4-Autopilot
make px4_sitl gazebo-classic_{self.world_name}
```

### Method 3: Environment Variables
```bash
cd /path/to/PX4-Autopilot
export PX4_SIM_MODEL=iris
export PX4_SIMULATOR=gazebo-classic
make px4_sitl gazebo-classic_{self.world_name}
```

## Connection

- **MAVLink UDP**: localhost:18570 (for QGroundControl)
- **Vehicle**: iris quadcopter spawns at origin (0, 0, 0.1)

## Files Generated

- `{self.world_name}.world` - Gazebo Classic world file
- `launch_{self.world_name}.sh` - Launch script
- `{self.world_name}_config.json` - Configuration backup
- `README.md` - This file
'''
        return readme_content

    def generate_files(self):
        """Generate all simulation files"""
        print(f"\n🏗️  Generating files for '{self.world_name}' world...")

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        files_created = []

        try:
            # Generate world file for Gazebo Classic
            world_file = os.path.join(self.output_dir, f"{self.world_name}.world")
            with open(world_file, 'w') as f:
                f.write(self.generate_world_file())
            files_created.append(world_file)
            print(f"✅ Created: {world_file}")

            # Generate launch script
            launch_file = os.path.join(self.output_dir, f"launch_{self.world_name}.sh")
            with open(launch_file, 'w') as f:
                f.write(self.generate_launch_script())
            os.chmod(launch_file, 0o755)  # Make executable
            files_created.append(launch_file)
            print(f"✅ Created: {launch_file}")

            # Generate config file
            config_file = os.path.join(self.output_dir, f"{self.world_name}_config.json")
            with open(config_file, 'w') as f:
                f.write(self.generate_config_file())
            files_created.append(config_file)
            print(f"✅ Created: {config_file}")

            # Generate README
            readme_file = os.path.join(self.output_dir, "README.md")
            with open(readme_file, 'w') as f:
                f.write(self.generate_readme())
            files_created.append(readme_file)
            print(f"✅ Created: {readme_file}")

            print(f"\n🎉 Successfully generated {len(files_created)} files!")
            print(f"📁 Output directory: {self.output_dir}")

            return files_created

        except Exception as e:
            print(f"❌ Error generating files: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Interactive Wall World Generator for PX4 Gazebo Classic')
    parser.add_argument('--batch', action='store_true', help='Skip interactive mode and use defaults')
    parser.add_argument('--config', type=str, help='Load configuration from JSON file')

    args = parser.parse_args()

    generator = WallWorldGenerator()

    if args.config:
        # Load from config file (implement if needed)
        print(f"Loading configuration from {args.config}...")
        # TODO: Implement config loading
    elif args.batch:
        # Use defaults for batch mode
        generator.world_name = "custom_wall"
        generator.wall_config = {
            'width': 5.0, 'height': 3.0, 'thickness': 0.2,
            'x': 5.0, 'y': 0.0,
            'color_name': 'White', 'color': (0.9, 0.9, 0.9, 1.0),
            'additional_walls': []
        }
        generator.output_dir = f"worlds/{generator.world_name}"
        generator.print_summary()
    else:
        # Interactive mode
        generator.get_user_inputs()

    # Generate files
    files_created = generator.generate_files()

    if files_created:
        print("\n" + "=" * 60)
        print("🚀 NEXT STEPS")
        print("=" * 60)
        print("1. Copy the world file to PX4-Autopilot:")
        print(f"   cp {generator.output_dir}/{generator.world_name}.world /path/to/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds/")
        print("\n2. Copy and run the launch script:")
        print(f"   cp {generator.output_dir}/launch_{generator.world_name}.sh /path/to/PX4-Autopilot/Tools/")
        print(f"   chmod +x /path/to/PX4-Autopilot/Tools/launch_{generator.world_name}.sh")
        print(f"   cd /path/to/PX4-Autopilot && ./Tools/launch_{generator.world_name}.sh")
        print("\n3. Alternative launch method:")
        print(f"   cd /path/to/PX4-Autopilot && make px4_sitl gazebo-classic_{generator.world_name}")
        print("\n4. Connect QGroundControl to udp://localhost:18570")
        print("\n📖 See README.md for detailed instructions")
    else:
        print("❌ Failed to generate files")
        sys.exit(1)

if __name__ == "__main__":
    main()
