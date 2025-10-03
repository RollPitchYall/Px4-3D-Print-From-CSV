# Px4-3D-Print-From-CSV

A Python module to control a PX4 drone using [MAVSDK Python](https://mavsdk.mavlink.io/main/en/index.html) in **offboard mode**, following waypoints defined in a CSV file. Can be used as a standalone script or imported as a module for integration into larger applications.

---

## Features

### Core Functionality
- **CSV-driven waypoint navigation** with automatic yaw calculation
- **PX4 Offboard Control** via MAVSDK for SITL and real hardware
- **Continuous movement** - commands future positions to prevent stopping
- **Configurable velocity limits** for predictable foam dispensing

### Safety & Monitoring  
- **Manual control override** - user must enable Offboard mode to start
- **Graceful shutdown** when switched out of Offboard (prints current CSV line)
- **Battery monitoring** with automatic RTL on low levels
- **Connection loss handling** via PX4 built-in failsafes
- **Progress tracking** with console output and telemetry monitoring

### Module Design
- **Standalone script** or **importable Python module**
- **Class-based architecture** with async/await patterns
- **Background monitoring tasks** for safety
- **Proper cleanup** and resource management

---

## Design Considerations & Architecture

### System Integration
This module operates within a larger 3D printing ecosystem. It can run on:
- **Companion computer** (recommended) - Better MAVLink reliability and faster communication
- **Ground-based computer** - Using wireless MAVLink connection

The module follows a **cooperative control philosophy** - it only assumes control when explicitly granted Offboard mode, and immediately relinquishes control if the flight mode is changed. This makes it flexible for integration with other flight management systems.

**Typical System Architecture:**
- **Flight Controller** (PX4) - Low-level flight control and safety
- **This Module** - High-level waypoint navigation and flight path execution
- **Extruder Control Module** - Compensates for drone movement during printing
- **Ground Control Station** - Mission planning and monitoring
- **Safety Pilot** - Ultimate authority and emergency override

### Drone Compatibility & Future Extensibility  
**Universal PX4 Compatibility:** Since all PX4 drones use the standardized MAVLink protocol, this module works with any PX4-based aircraft without modification.

**Performance Tuning:** Highly responsive drones may require PID tuning of the position control loops for smooth, predictable movement suitable for precision printing applications.

**Hardware Abstraction:** MAVSDK provides hardware abstraction by standardizing communication through MAVLink, making the module independent of specific flight controller hardware or drone configurations.

**Future Extensibility:** The class-based architecture allows easy extension for:
- Different coordinate systems (geographic, relative, etc.)
- Alternative autopilot systems (ArduPilot support via MAVLink)
- Custom payload integration (extruders, sensors, etc.)
- Advanced flight patterns beyond simple waypoints

**MAVSDK Compatibility:** Requires MAVSDK-Python 1.4.0+ with active development ensuring ongoing PX4 compatibility.

### Control Handoff & Safety Philosophy
**Pilot-in-Command Authority:** The safety pilot retains ultimate authority at all times. The module cannot force the aircraft into autonomous mode.

**Cooperative Control Protocol:**
1. **Module requests control** - Sends position setpoints but waits for pilot approval
2. **Pilot grants control** - Manually switches to Offboard mode in ground station
3. **Module assumes control** - Begins executing waypoint mission
4. **Immediate handoff** - Any flight mode change instantly returns control to pilot

**Emergency Override:** Pilot can regain control instantly via:
- Flight mode switch (Position, Altitude, Manual, etc.)
- RC transmitter override
- Ground control station mode change
- Kill switch activation

**No Automatic Resumption:** If control is lost, the module terminates completely - preventing unexpected autonomous behavior if accidentally switched back to Offboard mode.

### Safety Systems & Failsafes
**Multi-Layered Safety Architecture:**

**PX4 Flight Controller Level:**
- Low battery return-to-launch (RTL)
- Geofence violations
- RC signal loss failsafes
- Sensor failure detection

**Module Level:**
- Continuous flight mode monitoring
- Battery level monitoring with early warnings
- Position accuracy verification before waypoint advancement
- Graceful shutdown on any safety violation

**Communication Level:**
- MAVLink connection monitoring
- Automatic mission abort on connection loss
- Telemetry validation and timeout handling

**Operational Level:**
- Pre-flight system checks
- Waypoint validation (distance limits, altitude bounds)
- Progress logging for mission recovery
- Clear mission status reporting

### Performance Limitations & Considerations
**Flight Envelope Constraints:**
- Maximum waypoint separation: 3,281 feet (PX4 limitation)
- Recommended waypoint spacing: 0.1-50 meters for printing applications
- Altitude limits: Defined by airspace regulations and drone capabilities
- Velocity limits: Configurable but typically 1-5 m/s for precision work

**Precision & Accuracy:**
- Default position threshold: 2780mm (tunable)
- GPS accuracy dependent on satellite constellation and conditions
- Indoor operation requires alternative positioning system (VICON, OptiTrack, etc.)

**Environmental Considerations:**
- Wind resistance affects precision - recommend <15 mph winds
- Temperature affects battery performance and flight time
- Precipitation and visibility restrictions per aviation regulations

**Hardware Requirements:**
- Companion computer: Raspberry Pi 4 or equivalent (1GB+ RAM)
- MAVLink connection: Serial (preferred) or WiFi with <100ms latency
- Storage: Minimal (CSV files typically <1MB)

### Simulator to Real Aircraft Transition
**Phase 1: SITL (Software-in-the-Loop) Validation**
- Verify all waypoint navigation logic in Gazebo simulation
- Test failure modes and recovery procedures
- Validate CSV parsing and mission planning
- Confirm safety monitoring and shutdown procedures

**Phase 2: Hardware-in-the-Loop (HIL) Testing**
- Connect real flight controller to simulator
- Test actual MAVLink communication timing
- Validate companion computer integration
- Test with real RC transmitter and ground station

**Phase 3: Controlled Real Aircraft Testing**
- Start with tethered testing (safety rope)
- Small, simple flight patterns in controlled environment
- Gradually increase complexity and flight envelope
- Multiple safety observers and emergency procedures

**Phase 4: Operational Validation**
- Test in actual operating conditions
- Validate performance with payload (extruder system)
- Long-duration missions and battery management
- Integration with complete 3D printing workflow

**Regulatory Considerations:**
- FAA Part 107 compliance for commercial operations
- Airspace authorization for autonomous operations
- Risk assessment and mitigation documentation
- Insurance and liability considerations

---

## Requirements

- Companion Computer, WSL, or Linux Desktop
- Python **3.8+** ([Download](https://www.python.org/downloads/))
- PX4 firmware running on:
	- [PX4 SITL simulation](https://docs.px4.io/main/en/simulation/)
	- Or real drone hardware (via serial connection)

---

## Installation

### (Optional) Create and activate a virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
```

### Install MAVSDK

```sh
pip install mavsdk
```

If you're not using a virtual environment, you may need:

```sh
pip install mavsdk --break-system-packages
```

---

## Files in this Repository

- **`px4_csv_waypoints_with_mavsdk.py`** - Main module with `DroneController` class
- **`test_mission.py`** - Test script for drone connections and missions
- **`example_usage.py`** - Examples showing how to use the module
- **`coordinates.csv`** - Default waypoint file (small test pattern)
- **`coordinates2x.csv`** - 2x scale test pattern  
- **`coordinatesfast.csv`** - Fast test pattern (small file)

---

## Usage

## Usage Methods

### Method 1: Standalone Script
```sh
python px4_csv_waypoints_with_mavsdk.py
```

### Method 2: Use as Python Module

```python
import asyncio
from px4_csv_waypoints_with_mavsdk import DroneController

# Create controller
controller = DroneController(system_address="udpin://0.0.0.0:14540")

# Run mission
asyncio.run(controller.run_mission("my_waypoints.csv"))
```

### Method 3: Use Test Script

```sh
python test_mission.py
```

This provides interactive testing with error handling and timeouts.

### Connection Options

- **SITL Simulation**: `udpin://0.0.0.0:14540` (default)
- **Real Hardware**: `serial:///dev/ttyUSB0` (or your serial port)

### CSV File Requirements

- **Header row** is skipped (first line)
- **3 columns minimum**: N, E, D (additional columns ignored)
- **Comma-delimited** format
- **Numeric values** that can be converted to floats
- **Distance limits**: PX4 requires position changes < 3281 feet between waypoints 
   
3. **Run PX4:**
	 - SITL default connection: `udp://0.0.0.0:14540`
	 - For real hardware, use the appropriate serial connection for your device.

5. **Run the script:**

	Ensure that a CSV named coordinates.csv is in the same folder as the Python script, and that it is formatted correctly.

	 ```sh
	 python px4-csv-waypoints-with-mavsdk.py
	 ```
---

## Module API

### DroneController Class

```python
class DroneController:
    def __init__(self, system_address: str = "udpin://0.0.0.0:14540")
    async def run_mission(self, csv_filename: str = "coordinates.csv") -> None
    async def check_who_controls(self) -> None  # Background monitoring
    async def monitor_battery(self) -> None     # Background monitoring
    async def wait_until_at_waypoint(self, target_north, target_east, target_down, threshold=2780) -> Optional[object]
```

### Main Function

```python
def main(csv_file: str = "coordinates.csv", system_address: str = "udpin://0.0.0.0:14540") -> None
```

---

## Safety and Operation

### Offboard Mode Control
For safety, the module **does not force** the Flight Controller into Offboard mode. Instead:

1. **Script initializes** and sends initial offboard commands
2. **Waits for user** to manually switch to Offboard mode in QGroundControl
3. **Monitors flight mode** continuously via telemetry
4. **Begins mission** only after Offboard mode is confirmed
5. **Stops immediately** if user switches out of Offboard mode

### Critical Safety Behavior
When the user switches out of Offboard mode during flight:
- **Script immediately stops** sending position commands
- **Prints current CSV line number** where the mission was interrupted (e.g., "Flight interrupted at row 15, N=25, E=10, D=-5")
- **Gracefully shuts down** and terminates completely
- **Will NOT resume control** even if accidentally switched back to Offboard mode
- This prevents the drone from suddenly flying to a commanded position after manual control

### Safety Features
- **Battery monitoring** with automatic RTL on critical levels
- **Flight mode monitoring** with graceful shutdown on mode changes  
- **Connection loss handling** via PX4 built-in failsafes
- **Velocity limits** for predictable movement
- **Position thresholds** to confirm waypoint arrival
- **Progress tracking** - prints current CSV line number if mission is interrupted
- **Graceful shutdown** - script stops completely when switched out of Offboard mode and refuses to resume control even if accidentally switched back to Offboard

### QGroundControl Integration
<img width="873" height="539" alt="image" src="https://github.com/user-attachments/assets/7ef86019-ea41-4c40-b246-528303c288af" />

**Required steps:**
1. Connect QGroundControl to your drone/SITL
2. Run the Python script 
3. Wait for "Waiting for offboard control..." message
4. Switch to **Offboard** mode in QGroundControl
5. Mission will begin automatically

---

## Module Architecture

- **Class-based design** for reusability and state management
- **Async/await patterns** for concurrent operations  
- **Background monitoring** tasks for safety
- **Proper cleanup** and resource management
- **Type hints** and comprehensive documentation
- **Error handling** with graceful degradation

---

## Troubleshooting

**Script hangs at "Waiting for drone to connect":**
- Ensure PX4 SITL is running or drone is connected
- Check system address matches your setup

**"Waiting for offboard control" never progresses:**  
- Switch to Offboard mode in QGroundControl
- Ensure QGroundControl is connected to same drone

**Import errors when using as module:**
- Ensure MAVSDK is installed: `pip install mavsdk`
- Use underscores in filename: `px4_csv_waypoints_with_mavsdk.py`

**Mission stops unexpectedly:**
- Check console for "Flight interrupted at row X" message
- This indicates you (or failsafe) switched out of Offboard mode  
- This is intentional safety behavior - restart script to resume mission

**Script won't resume after switching back to Offboard:**
- This is a safety feature, not a bug
- The script terminates completely when Offboard mode is lost
- Restart the script if you want to restart the mission, or upload a new csv with waypoints beginning from the last waypoint.

