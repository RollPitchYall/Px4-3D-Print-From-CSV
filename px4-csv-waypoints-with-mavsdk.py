#!/usr/bin/env python3

# Code goals
# Control the Drone position based on a text file with coordinates ☑
# track telemetry to determine when coordinates are reached ☑
# Require the user to start the flight ☑
# allow a user to cancel and take manual control at any time ☑
# always command drone position to a future point so it doesnt slow and stop ☑
# monitor battery and return to home if low ☑
# log progress to console ☑
# set max velocity so foam is dispensed predictably ☑
# handle loss of offboard control gracefully ☑
# handle loss of controller connection gracefully ☑ (baked into PX4 failsafe settings)
# print real time distance from target position -> for foam arm attachment (sortof)

# ============================
# INSTALL & RUN INSTRUCTIONS
# ============================
# 1. Install Python 3.8+ (https://www.python.org/downloads/)
# 2. (Recommended) Create a virtual environment:
#      python3 -m venv venv
#      source venv/bin/activate
# 3. Install required Python packages:
#      pip install mavsdk
# 4. Ensure you have a PX4 SITL or real drone running and accessible.
#    - For simulation, you can use PX4 SITL (https://docs.px4.io/main/en/simulation/)
#    - Default connection is UDP: udpin://0.0.0.0:14540
# 5. Prepare a 'coordinates.csv' file in the same directory as this script.
#    - The CSV should have columns: N, E, D (in meters, NED frame)
# 6. Run the script:
#      python px4-csv-waypoints-with-mavsdk.py
# ============================

import csv
import math
import asyncio
import logging

from mavsdk.telemetry import FlightMode
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw

# Enable INFO level logging by default so that INFO messages are shown
logging.basicConfig(level=logging.INFO)

readyForOffboard = 0

async def run():
    """Does Offboard control using position NED coordinates."""
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540") #this would be serial for a real drone

    # Create background task for monitoring flight mode and battery level
    async def monitor(drone):
        control_task = asyncio.create_task(check_who_controls(drone))
        battery_task = asyncio.create_task(monitor_battery(drone))
        await asyncio.gather(control_task, battery_task)

    monitor_task = asyncio.create_task(monitor(drone))

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    # Set maximum velocity (m/s) so that movement is smooth and predictable
    await drone.param.set_param_float("MPC_XY_VEL_MAX", 1.0)
    await drone.param.set_param_float("MPC_Z_VEL_MAX_UP", 1.0)
    await drone.param.set_param_float("MPC_Z_VEL_MAX_DN", 1.0)
    print("Parameters updated!")

    await drone.telemetry.set_rate_position_velocity_ned(10.0)  # 50 Hz updates

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))#do something so that px4 knows we are ready for offboard

    while readyForOffboard == 0:
        print("-- Waiting for offboard control...")
        await asyncio.sleep(1)

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0)) # set current position to 0,0,0
    print("-- Arming")
    await drone.action.arm()
    print("-- Starting offboard")

    # import coordinates from csv
    with open('coordinates.csv', newline='') as file:
        reader = csv.reader(file)
        next(reader) #skips the labels
        n = 0.0
        e = 0.0
        d = 0.0
        for row in reader:
            # Save the current row number incase the program is stopped mid-flight
            row_num = reader.line_num
            dn = float(row[0]) - n
            de = float(row[1]) - e
            n = float(row[0])
            e = float(row[1])
            d = float(row[2])

            yaw = math.degrees(math.atan2(de, dn))
            print(f"Waypoint: N={n}m, E={e}m, D={d}m, Yaw={yaw}°")

            await drone.offboard.set_position_ned(PositionNedYaw(n, e, d, yaw))
            await wait_until_at_waypoint(drone, n, e, d)
            prev_n = n
            prev_e = e

            if readyForOffboard == 0:
                print(f"Flight interrupted at row {row_num}, N={n}, E={e}, D={d}.")
                break
    if readyForOffboard == 1:
        print("-- Returning home")
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, -1.0))
        await wait_until_at_waypoint(drone, 0.0, 0.0, -1.0, 0.5)
        await asyncio.sleep(5)
        print("-- Landing")
        await drone.action.land()
        await asyncio.sleep(10)
        print("-- Stopping offboard")
        #cancel offboard control
        try:
            await drone.offboard.stop()
        except OffboardError as error:
            print(
                f"Stopping offboard mode failed \
                    with error code: {error._result.result}"
            )

    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    print("-- Script completed successfully!")

async def check_who_controls(drone):
    """Monitor who is in control of the drone (Offboard or Manual)."""
    global readyForOffboard
    async for flightMode in drone.telemetry.flight_mode():
        # print(flightMode)
        # print(readyForOffboard)
        # print(type(readyForOffboard))
        if flightMode == FlightMode.OFFBOARD:
            if readyForOffboard == 0:
                print("-- Offboard has taken control")
                readyForOffboard = 1
        else:
            if readyForOffboard == 1:
                print("-- Offboard has lost control")
                readyForOffboard = 0

async def monitor_battery(drone):
    """Monitor the battery level and alert if low."""
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < 0.2:
            print(f"Warning: Low battery ({battery.remaining_percent*100:.1f}%)")
        #initiate rtl
        if battery.remaining_percent < 0.1:
            print("Critical battery level! Initiating Return to Launch (RTL).")
            await drone.action.return_to_launch()
            await wait_until_at_waypoint(drone, 0.0, 0.0, 0.0)  # Wait until back at home position
            await asyncio.sleep(5)  # Stabilize for a few seconds
            break
        await asyncio.sleep(5)  # Check battery level every 5 seconds



async def wait_until_at_waypoint(drone, target_north, target_east, target_down, threshold=0.15): # standard threshold is about 6 inches
    """
    Wait until the drone reaches the target waypoint within the specified threshold distance.

    Args:
        drone: The MAVSDK System instance
        target_north: Target North position in meters (NED frame)
        target_east: Target East position in meters (NED frame)
        target_down: Target Down position in meters (NED frame, negative = up)
        threshold: Distance threshold in meters (default: 0.15m)

    Returns:
        The final position when the waypoint is reached
    """
    print(f"-- Waiting to reach waypoint: N={target_north}m, E={target_east}m, D={target_down}m (threshold: {threshold}m)")

    while True:
        # Get only the latest telemetry reading
        position = await anext(drone.telemetry.position_velocity_ned())
        # Calculate distance to target
        dn = position.position.north_m - target_north
        de = position.position.east_m - target_east
        dd = position.position.down_m - target_down
        distance = (dn**2 + de**2 + dd**2) ** 0.5
        if distance < threshold:
            print(f"-- Reached waypoint! Final distance: {distance:.2f}m")
            return position
        if readyForOffboard == 0:
            break
        await asyncio.sleep(1/50)  # Check every 20ms


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
