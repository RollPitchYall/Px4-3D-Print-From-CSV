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

