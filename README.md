# Px4-3D-Print-From-CSV

A Python script to control a PX4 drone using [MAVSDK Python](https://mavsdk.mavlink.io/main/en/index.html) in **offboard mode**, following waypoints defined in a CSV file.

---

## Features

- **PX4 Offboard Control** via MAVSDK ☑
- Compatible with PX4 SITL simulation and real hardware ☑
- Reads coordinates from a CSV file ☑
- Controls the drone position based on the CSV coordinates ☑
- Calculates the drone's yaw angle based on the coordinates ☑ 
- Track telemetry to determine when coordinates are reached ☑
- Require the user to start the flight ☑
- Allow a user to cancel and override control at any time ☑
- Always command the drone's position to a future point so it doesn't slow and stop ☑
- Monitor battery and return to home if low ☑
- Print progress to console ☑
- Set max velocity so foam is dispensed predictably ☑
- Handle loss of offboard control gracefully ☑
- Handle loss of controller connection gracefully ☑ (baked into PX4 failsafe settings)

---

## Requirements

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

If you’re not using a virtual environment, you may need:

```sh
pip install mavsdk --break-system-packages
```

---

## Usage

1. **Prepare a CSV file** (use the included example or create your own) in the same directory as the script.  
	 The CSV must have the following columns:

	 ```
	 N,E,D
	 ```

	 Where:
	 - **N** = North (meters)
	 - **E** = East (meters)
	 - **D** = Down (meters, NED frame) (note that an increase in altitude is negative in the down frame) 

2. **Run PX4:**
	 - SITL default connection: `udp://0.0.0.0:14540`
	 - For real hardware, use the appropriate serial connection.

3. **Run the script:**

	 ```sh
	 python px4-csv-waypoints-with-mavsdk.py
	 ```

---
