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

	  The first row in the CSV (the header) is skipped, and all remaining rows must be filled with numerical values that can be converted to floats by the script. Columns past the first 3 are not read. The CSV delimiter should be a comma.
	  Additionally, PX4 requires that any commanded difference in distance be less than 3281 feet. 
   
3. **Run PX4:**
	 - SITL default connection: `udp://0.0.0.0:14540`
	 - For real hardware, use the appropriate serial connection for your device.

4. **Run the script:**

	Ensure that a CSV named coordinates.csv is in the same folder as the Python script, and that it is formatted correctly.

	 ```sh
	 python px4-csv-waypoints-with-mavsdk.py
	 ```
	
---

## Usage and Safety
	
	For safety, the script will not force the Flight Controller (simulated or real) into the Offboard control flight mode. The script initializes, sends an Offboard command which lets the flight controller know it's ready, then waits. The script tracks the MAVLink flight mode telemetry value, and once the user sets it to Offboard control, the script begins sending MAVLink position control packets. 

	Additionally, the script continuously monitors the drone's flight mode, and if the user manually switches the flight mode out of Offboard while the script is running, it will stop control and shut down. This makes it so that the user cannot accidentally switch the control back into offboard and have the drone unexpectedly fly away.

	
	<img width="873" height="539" alt="image" src="https://github.com/user-attachments/assets/7ef86019-ea41-4c40-b246-528303c288af" />

