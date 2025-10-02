# px4-csv-waypoints-with-mavsdk

A Python script to control a PX4 drone using [MAVSDK Python](https://mavsdk.mavlink.io/main/en/index.html) in **offboard mode**, following waypoints defined in a CSV file.

---

## Features

- **PX4 Offboard Control** via MAVSDK
- Reads waypoints from a CSV file
- Compatible with **PX4 SITL simulation** and **real hardware**

---

## Requirements

- Python **3.8+** ([Download](https://www.python.org/downloads/))
- PX4 firmware running on:
	- [PX4 SITL simulation](https://docs.px4.io/main/en/simulation/)
	- Real drone hardware (via serial connection)

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
