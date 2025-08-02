#!/usr/bin/env python3
"""
Update drone spawn pose in a Gazebo Classic world file based on wall config.
- Reads wall config JSON (position, dimensions)
- Updates or inserts <include> block for the drone in the .world file
- Ensures drone spawns in front of the wall, at a safe offset
"""
import json
import xml.etree.ElementTree as ET
import sys
import os

# --- CONFIGURABLE ---
CONFIG_PATH = "worlds/paint_wall/paint_wall_config.json"
WORLD_PATH = "worlds/paint_wall/paint_wall.world"
DRONE_MODEL_URI = "model://iris"
DRONE_NAME = "iris"
DRONE_OFFSET = 1.5  # meters in front of wall (distance from wall front face)


def load_wall_config(path):
    with open(path, 'r') as f:
        cfg = json.load(f)
    wall = cfg['main_wall']
    pos = wall['position']
    dims = wall['dimensions']
    return pos['x'], pos['y'], dims['width'], dims['height'], dims['thickness']


def compute_drone_pose(wall_x, wall_y, width, height, thickness, offset=1.5):
    # IMPORTANT: Understanding the coordinate system from the SDF file
    # Wall pose is at (7.0, 0.0, 2.5) with size <15.0 0.2 5.0>
    # This means:
    # - Wall extends in X-direction: 15.0m wide (from -0.5 to 14.5)
    # - Wall extends in Y-direction: 0.2m thick (from -0.1 to 0.1)
    # - Wall extends in Z-direction: 5.0m high (from 0.0 to 5.0)

    # Calculate wall boundaries in X-direction (wall width)
    wall_left_x = wall_x - (width / 2.0)      # Left edge: 7.0 - 7.5 = -0.5
    wall_right_x = wall_x + (width / 2.0)     # Right edge: 7.0 + 7.5 = 14.5

    # Calculate wall boundaries in Y-direction (wall thickness)
    wall_front_y = wall_y - (thickness / 2.0)  # Front face: 0.0 - 0.1 = -0.1
    wall_back_y = wall_y + (thickness / 2.0)   # Back face: 0.0 + 0.1 = 0.1

    # Position drone 1.5m in front of the wall's LEFT EDGE
    # The wall spans X from -0.5 to 14.5, so left edge is at X = -0.5
    # The wall front face is at Y = -0.1, so drone should be at Y = -0.1 - 1.5 = -1.6
    drone_x = wall_left_x            # At the LEFT EDGE of wall (X = -0.5)
    drone_y = wall_front_y - offset  # 1.5m in front of wall front face (Y = -1.6)
    drone_z = 1.0                    # 1m above ground for safety
    drone_yaw = 0.0                  # Face towards +Y (towards the wall)

    print(f"📐 Wall geometry (from SDF analysis):")
    print(f"   Wall center: ({wall_x:.2f}, {wall_y:.2f}, 2.5)")
    print(f"   Wall size: {width}m(X) × {thickness}m(Y) × {height}m(Z)")
    print(f"   Wall X span: {wall_left_x:.2f} to {wall_right_x:.2f}")
    print(f"   Wall Y span: {wall_front_y:.2f} to {wall_back_y:.2f}")
    print(f"🚁 Drone positioning:")
    print(f"   Drone spawn: ({drone_x:.2f}, {drone_y:.2f}, {drone_z:.2f})")
    print(f"   Distance from wall: {offset:.1f}m")
    print(f"   Position: At LEFT EDGE of wall (X={wall_left_x:.2f}), {offset:.1f}m in front")
    print(f"   Drone orientation: {drone_yaw:.0f}° (facing towards +Y, towards wall)")

    return drone_x, drone_y, drone_z, drone_yaw


def update_world_file(world_path, drone_pose, drone_name=DRONE_NAME, drone_uri=DRONE_MODEL_URI):
    tree = ET.parse(world_path)
    root = tree.getroot()
    world = root.find('world')
    if world is None:
        raise RuntimeError("No <world> element found in SDF")

    # Remove existing <include> for drone (if any)
    for inc in world.findall('include'):
        name = inc.find('name')
        uri = inc.find('uri')
        if (name is not None and name.text == drone_name) or (uri is not None and drone_name in uri.text):
            world.remove(inc)

    # Add new <include> for drone
    inc = ET.Element('include')
    uri = ET.SubElement(inc, 'uri')
    uri.text = drone_uri
    name = ET.SubElement(inc, 'name')
    name.text = drone_name
    pose = ET.SubElement(inc, 'pose')
    pose.text = f"{drone_pose[0]:.2f} {drone_pose[1]:.2f} {drone_pose[2]:.2f} 0 0 {drone_pose[3]:.2f}"
    world.append(inc)

    # Write back
    ET.indent(tree, space="  ")  # pretty print (Python 3.9+)
    tree.write(world_path, encoding='utf-8', xml_declaration=True)
    print(f"✅ Updated {world_path} with drone spawn at {pose.text}")


def main():
    if not os.path.exists(CONFIG_PATH) or not os.path.exists(WORLD_PATH):
        print(f"❌ Config or world file not found. Check paths.")
        sys.exit(1)
    wall_x, wall_y, width, height, thickness = load_wall_config(CONFIG_PATH)
    drone_pose = compute_drone_pose(wall_x, wall_y, width, height, thickness, DRONE_OFFSET)
    update_world_file(WORLD_PATH, drone_pose)

    # Print export commands for PX4_SPAWN_X/Y/Z/YAW
    print("\n# To launch PX4 SITL with the correct drone spawn location, run:")
    print(f"export PX4_SPAWN_X={drone_pose[0]:.2f}")
    print(f"export PX4_SPAWN_Y={drone_pose[1]:.2f}")
    print(f"export PX4_SPAWN_Z={drone_pose[2]:.2f}")
    print(f"export PX4_SPAWN_YAW={drone_pose[3]:.2f}")
    print("PX4_SITL_WORLD=custom_wall PX4_SIM_MODEL=iris make px4_sitl gazebo-classic")

    # Generate a launch script for convenience
    launch_script_path = "worlds/paint_wall/launch_with_spawn.sh"
    with open(launch_script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Auto-generated launch script with correct drone spawn position\n\n")
        f.write(f"export PX4_SPAWN_X={drone_pose[0]:.2f}\n")
        f.write(f"export PX4_SPAWN_Y={drone_pose[1]:.2f}\n")
        f.write(f"export PX4_SPAWN_Z={drone_pose[2]:.2f}\n")
        f.write(f"export PX4_SPAWN_YAW={drone_pose[3]:.2f}\n\n")
        f.write("echo \"🚀 Launching PX4 SITL with custom wall world...\"\n")
        f.write("echo \"   Drone spawn: ($PX4_SPAWN_X, $PX4_SPAWN_Y, $PX4_SPAWN_Z)\"\n")
        f.write("echo \"   Drone yaw: $PX4_SPAWN_YAW degrees\"\n")
        f.write("echo \"   World: custom_wall\"\n\n")
        f.write("PX4_SITL_WORLD=custom_wall PX4_SIM_MODEL=iris make px4_sitl gazebo-classic\n")

    print(f"\n✅ Created launch script: {launch_script_path}")
    print(f"   Make it executable: chmod +x {launch_script_path}")
    print(f"   Run: ./{launch_script_path}")

if __name__ == "__main__":
    main()
