#!/usr/bin/env python3
"""
Advanced Wall Spray Painting Mission using MAVSDK
Performs autonomous zig-zag pattern for wall painting simulation
Supports both VERTICAL and HORIZONTAL rectangular patterns
"""
import asyncio
import json
import math
from mavsdk import System
from mavsdk.offboard import PositionNedYaw, VelocityNedYaw

class AdvancedWallSprayPainter:
    def __init__(self):
        self.drone = System()
        self.wall_config = None
        self.spray_waypoints = []
        self.pattern_type = None  # 'vertical' or 'horizontal'
        self.takeoff_position = None   # Store original takeoff position for return

        # Configurable speed parameters (meters/second)
        self.vertical_speed = 1.0      # Speed for up/down movements
        self.horizontal_speed = 0.8    # Speed for sideways movements
        self.positioning_speed = 1.5   # Speed for moving to start position
        self.hover_time = 2.0          # Hover time at each waypoint (seconds)

        # Movement precision
        self.waypoint_tolerance = 0.3  # Distance tolerance to consider waypoint reached (meters)

    def select_pattern_type(self):
        """Ask user to select pattern type"""
        print("\n🎨 Wall Spray Painting Pattern Selection")
        print("=" * 50)
        print("1. VERTICAL Pattern   - Paint up/down first, then move sideways")
        print("2. HORIZONTAL Pattern - Paint left/right first, then move up/down")
        print("=" * 50)

        while True:
            try:
                choice = input("Select pattern type (1 for Vertical, 2 for Horizontal): ").strip()
                if choice == '1':
                    self.pattern_type = 'vertical'
                    print("✅ Selected: VERTICAL rectangular pattern")
                    break
                elif choice == '2':
                    self.pattern_type = 'horizontal'
                    print("✅ Selected: HORIZONTAL rectangular pattern")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1 or 2.")
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user")
                return False
        return True

    def configure_speeds(self, vertical_speed=1.0, horizontal_speed=0.8, positioning_speed=1.5, hover_time=2.0):
        """Configure movement speeds for different actions"""
        self.vertical_speed = vertical_speed
        self.horizontal_speed = horizontal_speed
        self.positioning_speed = positioning_speed
        self.hover_time = hover_time

        print(f"⚡ Speed Configuration:")
        print(f"   - Vertical speed: {self.vertical_speed:.1f} m/s")
        print(f"   - Horizontal speed: {self.horizontal_speed:.1f} m/s")
        print(f"   - Positioning speed: {self.positioning_speed:.1f} m/s")
        print(f"   - Hover time: {self.hover_time:.1f} seconds")

    async def connect(self):
        """Connect to the drone"""
        print("🔗 Connecting to drone at udp://:14540...")
        await self.drone.connect(system_address="udp://:14540")

        # Wait for connection
        print("⏳ Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("✅ Drone connected!")
                break

    def load_wall_config(self):
        """Load wall configuration from JSON file"""
        try:
            with open('worlds/paint_wall/paint_wall_config.json', 'r') as f:
                config = json.load(f)
                # Extract wall info from the nested structure
                self.wall_config = {
                    'width': config['main_wall']['dimensions']['width'],
                    'height': config['main_wall']['dimensions']['height'],
                    'thickness': config['main_wall']['dimensions']['thickness'],
                    'position': config['main_wall']['position']
                }
            print(f"📐 Wall loaded: {self.wall_config['width']}m × {self.wall_config['height']}m")
            return True
        except FileNotFoundError:
            print("❌ Wall config file not found. Please run the wall generator first.")
            return False
        except KeyError as e:
            print(f"❌ Invalid wall config format: missing key {e}")
            return False

    def calculate_spray_waypoints_vertical(self, current_ned_position):
        """Calculate VERTICAL rectangular pattern waypoints (paint up/down first, then move sideways)"""
        # Constants for spray pattern
        STRIPE_WIDTH = 0.4   # Width of each spray stripe (meters)
        SPRAY_HEIGHT_START = 0.5  # Starting height above ground

        # Wall configuration from JSON
        wall_width = self.wall_config['width']
        wall_height = self.wall_config['height']

        print(f"🏗️ VERTICAL Pattern - Wall dimensions: {wall_width}m × {wall_height}m")
        print(f"🚁 Starting from drone spawn position: ({current_ned_position.north_m:.2f}, {current_ned_position.east_m:.2f}, {current_ned_position.down_m:.2f})")

        # Use current drone position as the starting point
        start_x = current_ned_position.north_m  # Keep X constant (North direction - pitch)
        start_y = current_ned_position.east_m   # Move along Y (East direction - roll)

        # Calculate number of stripes needed to cover the wall width
        num_stripes = int(wall_width / STRIPE_WIDTH) + 1

        waypoints = []
        going_up = True

        # Calculate spray heights in NED coordinates (negative = above ground)
        ground_level = 0.0  # Ground level in NED coordinates
        spray_bottom_z = ground_level - SPRAY_HEIGHT_START  # Start height above ground (0.5m)
        spray_top_z = ground_level - wall_height  # Top of wall (5.0m above ground)

        print(f"🎯 Spray heights:")
        print(f"   - Bottom Z = {spray_bottom_z:.2f}m (height: {-spray_bottom_z:.2f}m above ground)")
        print(f"   - Top Z = {spray_top_z:.2f}m (height: {-spray_top_z:.2f}m above ground)")

        print(f"🎨 Generating {num_stripes} vertical stripes with {STRIPE_WIDTH}m width each...")
        print(f"   Drone spawn: X={start_x:.2f}, Y={start_y:.2f}")
        print(f"   Wall spans along Y-direction (15m width)")
        print(f"   Moving along Y-direction (roll axis - wall width)")

        current_y = start_y  # Track current Y position

        for stripe in range(num_stripes):
            # Calculate Y position for this stripe (move along the wall width - roll axis)
            target_y = start_y + (stripe * STRIPE_WIDTH)

            # Stop if we've covered the wall width
            if stripe * STRIPE_WIDTH > wall_width:
                print(f"   Stripe {stripe + 1}: Covered full wall width, stopping")
                break

            print(f"   Stripe {stripe + 1}: Y = {target_y:.2f} (offset: +{stripe * STRIPE_WIDTH:.2f}m from start)")

            if going_up:
                # Phase 1: Move vertically UP first (at current Y position)
                waypoints.append({
                    'x': start_x,
                    'y': current_y,  # Stay at current Y position
                    'z': spray_top_z,  # Move UP to top
                    'yaw': 0.0,
                    'action': 'move_up_vertical',
                    'stripe': stripe + 1
                })

                # Phase 2: Move horizontally along Y-axis (at top height)
                waypoints.append({
                    'x': start_x,
                    'y': target_y,  # Move to target Y position
                    'z': spray_top_z,  # Stay at top height
                    'yaw': 0.0,
                    'action': 'move_horizontal_top',
                    'stripe': stripe + 1
                })

                # Phase 3: Move vertically DOWN (at new Y position)
                waypoints.append({
                    'x': start_x,
                    'y': target_y,  # Stay at target Y position
                    'z': spray_bottom_z,  # Move DOWN to bottom
                    'yaw': 0.0,
                    'action': 'move_down_vertical',
                    'stripe': stripe + 1
                })

            else:
                # Phase 1: Move vertically DOWN first (at current Y position)
                waypoints.append({
                    'x': start_x,
                    'y': current_y,  # Stay at current Y position
                    'z': spray_bottom_z,  # Move DOWN to bottom
                    'yaw': 0.0,
                    'action': 'move_down_vertical',
                    'stripe': stripe + 1
                })

                # Phase 2: Move horizontally along Y-axis (at bottom height)
                waypoints.append({
                    'x': start_x,
                    'y': target_y,  # Move to target Y position
                    'z': spray_bottom_z,  # Stay at bottom height
                    'yaw': 0.0,
                    'action': 'move_horizontal_bottom',
                    'stripe': stripe + 1
                })

                # Phase 3: Move vertically UP (at new Y position)
                waypoints.append({
                    'x': start_x,
                    'y': target_y,  # Stay at target Y position
                    'z': spray_top_z,  # Move UP to top
                    'yaw': 0.0,
                    'action': 'move_up_vertical',
                    'stripe': stripe + 1
                })

            # Update current Y position for next stripe
            current_y = target_y
            going_up = not going_up  # Alternate direction for next stripe

        return waypoints

    def calculate_spray_waypoints_horizontal(self, current_ned_position):
        """Calculate HORIZONTAL rectangular pattern waypoints (paint left/right first, then move up/down)"""
        # Constants for spray pattern
        STRIPE_HEIGHT = 0.4   # Height of each spray stripe (meters)
        SPRAY_HEIGHT_START = 0.5  # Starting height above ground

        # Wall configuration from JSON
        wall_width = self.wall_config['width']
        wall_height = self.wall_config['height']

        print(f"🏗️ HORIZONTAL Pattern - Wall dimensions: {wall_width}m × {wall_height}m")
        print(f"🚁 Starting from drone spawn position: ({current_ned_position.north_m:.2f}, {current_ned_position.east_m:.2f}, {current_ned_position.down_m:.2f})")

        # Use current drone position as the starting point
        start_x = current_ned_position.north_m  # Keep X constant (North direction - pitch)
        start_y = current_ned_position.east_m   # Move along Y (East direction - roll)

        # Calculate number of horizontal stripes needed to cover the wall height
        num_stripes = int(wall_height / STRIPE_HEIGHT)
        if wall_height % STRIPE_HEIGHT > 0:
            num_stripes += 1  # Add one more stripe for partial coverage

        # Ensure we don't exceed reasonable limits
        max_stripes = int(wall_height / STRIPE_HEIGHT) + 1
        num_stripes = min(num_stripes, max_stripes)

        waypoints = []
        going_right = True  # Start by going RIGHT since drone spawns at left side of wall

        # Calculate spray heights in NED coordinates (negative = above ground)
        ground_level = 0.0  # Ground level in NED coordinates
        spray_bottom_z = ground_level - SPRAY_HEIGHT_START  # Start height above ground (0.5m)

        # Calculate Y positions for wall coverage
        wall_left_y = start_y  # Start from drone spawn position
        wall_right_y = start_y + wall_width  # End position

        print(f"🎯 Spray positions:")
        print(f"   - Left Y = {wall_left_y:.2f}m")
        print(f"   - Right Y = {wall_right_y:.2f}m")
        print(f"   - Wall width coverage: {wall_width}m")

        print(f"🎨 Generating up to {num_stripes} horizontal stripes with {STRIPE_HEIGHT}m height each...")
        print(f"   Drone spawn: X={start_x:.2f}, Y={start_y:.2f}")
        print(f"   Moving vertically along Z-direction (wall height)")
        print(f"   Wall height limit: {wall_height}m")
        print(f"   Start height: {SPRAY_HEIGHT_START}m above ground")
        print(f"   Maximum height: {wall_height}m above ground")

        current_z = spray_bottom_z  # Track current Z position
        current_y = wall_left_y     # Track current Y position (start at left edge)

        for stripe in range(num_stripes):
            # Calculate height for this stripe
            stripe_height_from_bottom = stripe * STRIPE_HEIGHT

            # Stop if we've covered the wall height
            if stripe_height_from_bottom > wall_height:
                print(f"   Stripe {stripe + 1}: Would exceed wall height ({stripe_height_from_bottom:.2f}m > {wall_height}m), stopping")
                break

            # Calculate Z position for this stripe (move up the wall)
            # Ensure we don't go higher than the wall height
            max_height_from_bottom = min(stripe_height_from_bottom, wall_height)
            target_z = spray_bottom_z - max_height_from_bottom

            print(f"   Stripe {stripe + 1}: Z = {target_z:.2f} (height: {-target_z:.2f}m above ground, max: {wall_height}m)")

            if going_right:
                # Phase 1: Move vertically UP first (at current left position)
                waypoints.append({
                    'x': start_x,
                    'y': wall_left_y,  # Stay at left position
                    'z': target_z,  # Move UP to target height
                    'yaw': 0.0,
                    'action': 'move_up_left',
                    'stripe': stripe + 1
                })

                # Phase 2: Move horizontally RIGHT (at new Z position)
                waypoints.append({
                    'x': start_x,
                    'y': wall_right_y,  # Move RIGHT to end of wall
                    'z': target_z,  # Stay at target height
                    'yaw': 0.0,
                    'action': 'move_right_horizontal',
                    'stripe': stripe + 1
                })

            else:
                # Phase 1: Move vertically UP first (at current right position)
                waypoints.append({
                    'x': start_x,
                    'y': wall_right_y,  # Stay at right position
                    'z': target_z,  # Move UP to target height
                    'yaw': 0.0,
                    'action': 'move_up_right',
                    'stripe': stripe + 1
                })

                # Phase 2: Move horizontally LEFT (at new Z position)
                waypoints.append({
                    'x': start_x,
                    'y': wall_left_y,  # Move LEFT to start of wall
                    'z': target_z,  # Stay at target height
                    'yaw': 0.0,
                    'action': 'move_left_horizontal',
                    'stripe': stripe + 1
                })

            # Update current positions for next stripe
            current_z = target_z
            if going_right:
                current_y = wall_right_y  # Now at right edge
            else:
                current_y = wall_left_y   # Now at left edge
            going_right = not going_right  # Alternate direction for next stripe

        return waypoints

    def calculate_spray_waypoints(self, current_ned_position):
        """Calculate spray pattern waypoints based on selected pattern type"""
        if self.pattern_type == 'vertical':
            waypoints = self.calculate_spray_waypoints_vertical(current_ned_position)
        elif self.pattern_type == 'horizontal':
            waypoints = self.calculate_spray_waypoints_horizontal(current_ned_position)
        else:
            print("❌ No pattern type selected!")
            return []

        self.spray_waypoints = waypoints
        print(f"📋 Generated {len(waypoints)} spray waypoints for {self.pattern_type.upper()} pattern")

        if waypoints:
            print(f"🔍 First waypoint: ({waypoints[0]['x']:.2f}, {waypoints[0]['y']:.2f}, {waypoints[0]['z']:.2f}) - {waypoints[0]['action']}")
            print(f"🔍 Last waypoint: ({waypoints[-1]['x']:.2f}, {waypoints[-1]['y']:.2f}, {waypoints[-1]['z']:.2f}) - {waypoints[-1]['action']}")

        return waypoints

    async def move_to_waypoint_with_speed(self, target_waypoint, speed, movement_type="positioning"):
        """Move to a waypoint with specified speed using velocity control"""
        print(f"🎯 Moving to waypoint with {speed:.1f} m/s ({movement_type})")
        print(f"   Target: ({target_waypoint['x']:.2f}, {target_waypoint['y']:.2f}, {target_waypoint['z']:.2f})")

        # Get current position
        async for position_ned in self.drone.telemetry.position_velocity_ned():
            current_pos = position_ned.position
            break

        target_reached = False
        max_time = 30.0  # Maximum time to reach waypoint (seconds)
        start_time = asyncio.get_event_loop().time()

        while not target_reached and (asyncio.get_event_loop().time() - start_time) < max_time:
            # Get current position
            async for position_ned in self.drone.telemetry.position_velocity_ned():
                current_pos = position_ned.position
                break

            # Calculate distance and direction to target
            dx = target_waypoint['x'] - current_pos.north_m
            dy = target_waypoint['y'] - current_pos.east_m
            dz = target_waypoint['z'] - current_pos.down_m

            distance = math.sqrt(dx*dx + dy*dy + dz*dz)

            # Check if we've reached the target
            if distance < self.waypoint_tolerance:
                target_reached = True
                print(f"   ✅ Reached waypoint (distance: {distance:.2f}m)")
                break

            # Calculate velocity components
            if distance > 0:
                # Normalize direction vector
                vx = (dx / distance) * speed
                vy = (dy / distance) * speed
                vz = (dz / distance) * speed

                # Limit velocity components to prevent overshoot
                max_component_speed = speed * 0.8
                vx = max(-max_component_speed, min(max_component_speed, vx))
                vy = max(-max_component_speed, min(max_component_speed, vy))
                vz = max(-max_component_speed, min(max_component_speed, vz))

                # Slow down when approaching target
                if distance < 2.0:
                    slowdown_factor = max(0.3, distance / 2.0)
                    vx *= slowdown_factor
                    vy *= slowdown_factor
                    vz *= slowdown_factor

                # Send velocity command
                await self.drone.offboard.set_velocity_ned(
                    VelocityNedYaw(vx, vy, vz, 0.0)
                )

            await asyncio.sleep(0.1)  # 10Hz control loop

        if not target_reached:
            print(f"   ⚠️ Timeout reaching waypoint, distance: {distance:.2f}m")

        # Stop movement and hold position
        await self.drone.offboard.set_position_ned(
            PositionNedYaw(target_waypoint['x'], target_waypoint['y'], target_waypoint['z'], 0.0)
        )

        # Hover at waypoint
        hover_steps = int(self.hover_time * 10)  # Convert to 0.1s steps
        for step in range(hover_steps):
            await self.drone.offboard.set_position_ned(
                PositionNedYaw(target_waypoint['x'], target_waypoint['y'], target_waypoint['z'], 0.0)
            )
            await asyncio.sleep(0.1)

        return target_reached

    async def arm_and_setup_offboard(self):
        """Arm the drone and setup offboard mode"""
        # Wait for drone to be ready
        print("⏳ Waiting for drone to be ready...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("✅ Drone ready for arming")
                break

        # Get current position
        print("📍 Getting current position for offboard...")
        current_position = None
        async for position_ned in self.drone.telemetry.position_velocity_ned():
            current_position = position_ned.position
            print(f"   Current NED: ({current_position.north_m:.2f}, {current_position.east_m:.2f}, {current_position.down_m:.2f})")
            break

        # Start sending setpoints to make drone armable in OFFBOARD mode
        print("🎮 Starting offboard setpoint stream...")
        await self.drone.offboard.set_position_ned(
            PositionNedYaw(current_position.north_m, current_position.east_m, current_position.down_m, 0.0)
        )

        # Start offboard mode
        print("🚀 Starting offboard mode...")
        try:
            await self.drone.offboard.start()
            print("✅ Offboard mode started")
        except Exception as e:
            print(f"❌ Failed to start offboard: {e}")
            raise e

        # Keep sending setpoints for a moment to establish the stream
        print("📡 Establishing setpoint stream...")
        for i in range(10):
            await self.drone.offboard.set_position_ned(
                PositionNedYaw(current_position.north_m, current_position.east_m, current_position.down_m, 0.0)
            )
            await asyncio.sleep(0.1)

        # Check if drone is now armable
        async for health in self.drone.telemetry.health():
            if health.is_armable:
                print("✅ Drone is now armable")
                break
            else:
                print("⚠️ Drone still not armable")

        print("🔧 Arming drone...")
        try:
            await self.drone.action.arm()
            print("✅ Drone armed successfully")
        except Exception as e:
            print(f"❌ Failed to arm drone: {e}")
            raise e

        # Instead of using action.takeoff(), let's use offboard to takeoff
        print("🚁 Taking off using offboard control...")
        takeoff_altitude = -2.0  # 2 meters above ground (negative in NED)

        # Gradually climb to takeoff altitude
        for step in range(20):
            target_z = current_position.down_m + (takeoff_altitude * step / 20)
            await self.drone.offboard.set_position_ned(
                PositionNedYaw(current_position.north_m, current_position.east_m, target_z, 0.0)
            )
            await asyncio.sleep(0.2)

        print("✅ Takeoff completed using offboard control")

        # Store the takeoff position for return later
        self.takeoff_position = {
            'x': current_position.north_m,
            'y': current_position.east_m,
            'z': takeoff_altitude,  # Use the takeoff altitude we climbed to
            'yaw': 0.0
        }
        print(f"📍 Takeoff position stored: ({self.takeoff_position['x']:.2f}, {self.takeoff_position['y']:.2f}, {self.takeoff_position['z']:.2f})")

        return current_position

    async def move_to_wall_start_position(self):
        """Move drone to the starting position for wall spraying using speed control"""
        if not self.spray_waypoints:
            print("❌ No waypoints calculated yet!")
            return

        # Get current position
        async for position_ned in self.drone.telemetry.position_velocity_ned():
            current_pos = position_ned.position
            print(f"🚁 Current position: ({current_pos.north_m:.2f}, {current_pos.east_m:.2f}, {current_pos.down_m:.2f})")
            break

        # Get the first waypoint as our starting position
        start_waypoint = self.spray_waypoints[0]

        print(f"🎯 Moving to spray start position with {self.positioning_speed:.1f} m/s:")
        print(f"   Target: ({start_waypoint['x']:.2f}, {start_waypoint['y']:.2f}, {start_waypoint['z']:.2f})")

        # Use speed-controlled movement to reach start position
        success = await self.move_to_waypoint_with_speed(start_waypoint, self.positioning_speed, "initial_positioning")

        if success:
            print("✅ Ready to start spray painting pattern!")
        else:
            print("⚠️ Reached start position with timeout, continuing...")

        print("✅ Ready to start spray painting pattern!")

    async def execute_spray_pattern(self):
        """Execute the spray painting pattern with speed control"""
        print(f"🎨 Starting speed-controlled {self.pattern_type.upper()} spray painting mission...")

        for i, waypoint in enumerate(self.spray_waypoints):
            stripe_info = f"[Stripe {waypoint.get('stripe', '?')}]" if 'stripe' in waypoint else ""
            print(f"📍 Moving to waypoint {i+1}/{len(self.spray_waypoints)} {stripe_info}: {waypoint['action']}")

            # Determine speed based on movement type for both vertical and horizontal patterns
            if 'vertical' in waypoint['action'] or 'up' in waypoint['action'] or 'down' in waypoint['action']:
                speed = self.vertical_speed
                movement_type = "vertical_painting"
                print(f"   🔄 Vertical movement at {speed:.1f} m/s")
            elif 'horizontal' in waypoint['action'] or 'right' in waypoint['action'] or 'left' in waypoint['action']:
                speed = self.horizontal_speed
                movement_type = "horizontal_positioning"
                print(f"   ↔️ Horizontal movement at {speed:.1f} m/s")
            else:
                speed = self.positioning_speed
                movement_type = "general_positioning"
                print(f"   📍 General movement at {speed:.1f} m/s")

            # Move to waypoint with appropriate speed
            success = await self.move_to_waypoint_with_speed(waypoint, speed, movement_type)

            if not success:
                print(f"   ⚠️ Waypoint {i+1} reached with timeout, continuing...")

        print(f"✅ Speed-controlled {self.pattern_type.upper()} spray painting pattern completed!")

    async def return_to_takeoff_position(self):
        """Return drone to original takeoff position"""
        if not self.takeoff_position:
            print("⚠️ No takeoff position stored, skipping return to home")
            return

        print("🏠 Returning to takeoff position...")
        print(f"   Target: ({self.takeoff_position['x']:.2f}, {self.takeoff_position['y']:.2f}, {self.takeoff_position['z']:.2f})")

        # Get current position for reference
        async for position_ned in self.drone.telemetry.position_velocity_ned():
            current_pos = position_ned.position
            print(f"   Current: ({current_pos.north_m:.2f}, {current_pos.east_m:.2f}, {current_pos.down_m:.2f})")
            break

        # Calculate distance to takeoff position
        dx = self.takeoff_position['x'] - current_pos.north_m
        dy = self.takeoff_position['y'] - current_pos.east_m
        dz = self.takeoff_position['z'] - current_pos.down_m
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)

        print(f"   Distance to takeoff position: {distance:.2f}m")

        # Use speed-controlled movement to return home
        success = await self.move_to_waypoint_with_speed(
            self.takeoff_position,
            self.positioning_speed,
            "return_to_takeoff"
        )

        if success:
            print("✅ Successfully returned to takeoff position!")
        else:
            print("⚠️ Returned to takeoff area with timeout")

        # Hold position briefly before landing
        print("⏸️ Holding position for 3 seconds before landing...")
        for i in range(30):  # 3 seconds at 10Hz
            await self.drone.offboard.set_position_ned(
                PositionNedYaw(
                    self.takeoff_position['x'],
                    self.takeoff_position['y'],
                    self.takeoff_position['z'],
                    self.takeoff_position['yaw']
                )
            )
            await asyncio.sleep(0.1)

    async def land_and_cleanup(self):
        """Land the drone and cleanup"""
        print("🛬 Landing at takeoff position...")

        # Get current position to confirm we're at takeoff location
        async for position_ned in self.drone.telemetry.position_velocity_ned():
            current_pos = position_ned.position
            if self.takeoff_position:
                distance_from_takeoff = math.sqrt(
                    (current_pos.north_m - self.takeoff_position['x'])**2 +
                    (current_pos.east_m - self.takeoff_position['y'])**2
                )
                print(f"   Distance from takeoff position: {distance_from_takeoff:.2f}m")
            break

        # Stop offboard mode before landing to avoid conflicts
        try:
            print("⏹️ Stopping offboard mode before landing...")
            await self.drone.offboard.stop()
            print("✅ Offboard mode stopped successfully")
        except Exception as e:
            print(f"⚠️ Warning stopping offboard (this is normal): {e}")

        # Now land using action command
        try:
            await self.drone.action.land()
            print("✅ Landing command sent")
        except Exception as e:
            print(f"⚠️ Landing command error: {e}")

        # Wait for landing to complete
        print("⏳ Waiting for landing to complete...")
        await asyncio.sleep(8)  # Give more time for landing

        # Check final status
        await self.check_drone_status()

        print("✅ Landing sequence completed")

    async def check_drone_status(self):
        """Check current drone status for diagnostics"""
        try:
            # Check armed state
            async for armed in self.drone.telemetry.armed():
                print(f"🔧 Drone armed: {armed.is_armed}")
                break

            # Check flight mode
            async for flight_mode in self.drone.telemetry.flight_mode():
                print(f"🛫 Flight mode: {flight_mode}")
                break

        except Exception as e:
            print(f"⚠️ Status check error: {e}")

    async def run_mission(self):
        """Run the complete spray painting mission"""
        try:
            # Select pattern type first
            if not self.select_pattern_type():
                return

            # Configure speed settings based on pattern type
            print("⚙️ Configuring movement speeds...")
            if self.pattern_type == 'vertical':
                # Optimized speeds for vertical pattern
                self.configure_speeds(
                    vertical_speed=1.2,      # Faster vertical movements for painting
                    horizontal_speed=0.8,    # Slower horizontal movements for precision
                    positioning_speed=1.5,   # Fast positioning movements
                    hover_time=1.5           # Hover time at each waypoint
                )
            elif self.pattern_type == 'horizontal':
                # Optimized speeds for horizontal pattern
                self.configure_speeds(
                    vertical_speed=0.8,      # Slower vertical positioning for precision
                    horizontal_speed=1.2,    # Faster horizontal movements for painting
                    positioning_speed=1.5,   # Fast positioning movements
                    hover_time=1.5           # Hover time at each waypoint
                )

            # Connect to drone
            await self.connect()

            # Load wall configuration
            if not self.load_wall_config():
                return

            # Get current position first
            print("📍 Getting current position...")
            async for position in self.drone.telemetry.position():
                print(f"   GPS: ({position.latitude_deg}, {position.longitude_deg}, {position.absolute_altitude_m}m)")
                break

            async for position_ned in self.drone.telemetry.position_velocity_ned():
                print(f"   NED: ({position_ned.position.north_m:.1f}, {position_ned.position.east_m:.1f}, {position_ned.position.down_m:.1f})")
                current_ned_position = position_ned.position
                break

            # Calculate spray waypoints
            self.calculate_spray_waypoints(current_ned_position)

            # Arm and setup offboard
            await self.arm_and_setup_offboard()

            # Move to wall start position
            await self.move_to_wall_start_position()

            # Execute spray pattern
            await self.execute_spray_pattern()

            # Return to takeoff position
            await self.return_to_takeoff_position()

            # Land and cleanup
            await self.land_and_cleanup()

            print("🎉 Mission completed successfully!")

        except Exception as e:
            print(f"❌ Mission failed: {e}")
            # Try to return to takeoff position and land safely
            try:
                if self.takeoff_position:
                    print("🚨 Emergency return to takeoff position...")
                    await self.return_to_takeoff_position()

                # Emergency landing sequence
                print("🚨 Emergency landing sequence...")
                try:
                    await self.drone.offboard.stop()
                    print("✅ Emergency offboard stop successful")
                except Exception as stop_error:
                    print(f"⚠️ Emergency offboard stop warning: {stop_error}")

                await self.drone.action.land()
                print("✅ Emergency landing command sent")

            except Exception as land_error:
                print(f"❌ Emergency landing failed: {land_error}")
                pass

async def main():
    painter = AdvancedWallSprayPainter()
    await painter.run_mission()

if __name__ == "__main__":
    asyncio.run(main())
