#!/usr/bin/env python3
"""
PX4 CSV Waypoint Navigation Module

This module provides functionality to control a PX4 drone using waypoints
loaded from CSV files via MAVSDK. It can be used as a standalone script
or imported as a module for integration into other applications.

Usage Instructions Available on Github:
https://github.com/RollPitchYall/Px4-3D-Print-From-CSV/tree/main

Author: RollPitchYall
"""

import asyncio
import csv
import logging
import math
from typing import Optional

from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw
from mavsdk.telemetry import FlightMode

# Configure logging
logging.basicConfig(level=logging.INFO)


class DroneController:
    """
    A controller class for PX4 drone waypoint navigation using MAVSDK.
    
    This class encapsulates all drone control functionality including connection,
    waypoint navigation, monitoring, and safety features.
    """
    
    def __init__(self, system_address: str = "udpin://0.0.0.0:14540"):
        """
        Initialize the drone controller.
        
        Args:
            system_address: The connection address for the drone system
        """
        self.system_address = system_address
        self.ready_for_offboard = False
        self.drone: Optional[System] = None
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def run_mission(self, csv_filename: str = "coordinates.csv") -> None:
        """
        Execute the complete drone mission using waypoints from a CSV file.
        
        Args:
            csv_filename: Path to the CSV file containing waypoints
        """
        self.drone = System()
        await self.drone.connect(system_address=self.system_address)

        # Create background task for monitoring flight mode and battery level
        async def monitor():
            control_task = asyncio.create_task(self.check_who_controls())
            battery_task = asyncio.create_task(self.monitor_battery())
            await asyncio.gather(control_task, battery_task)

        self.monitor_task = asyncio.create_task(monitor())

        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("-- Connected to drone!")
                break

        print("Waiting for drone to have a global position estimate...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("-- Global position estimate OK")
                break

        # Set maximum velocity (m/s) so that movement is smooth and predictable
        await self.drone.param.set_param_float("MPC_XY_VEL_MAX", 1.0)
        await self.drone.param.set_param_float("MPC_Z_VEL_MAX_UP", 1.0)
        await self.drone.param.set_param_float("MPC_Z_VEL_MAX_DN", 1.0)
        print("Max Speed Parameters updated!")

        await self.drone.telemetry.set_rate_position_velocity_ned(10.0)  # 10 Hz updates

        print("-- Setting initial setpoint")
        await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

        while not self.ready_for_offboard:
            print("-- Waiting for offboard control...")
            await asyncio.sleep(1)

        await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
        print("-- Arming")
        await self.drone.action.arm()
        print("-- Starting offboard")

        # Load and navigate waypoints from CSV
        await self._navigate_waypoints_from_csv(csv_filename)

        if self.ready_for_offboard:
            await self._return_home_and_land()

        # Clean up monitoring task
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        # Proper cleanup and disconnection
        print("-- Cleaning up and disconnecting...")
        
        # Stop offboard mode if still active
        if self.ready_for_offboard:
            try:
                await self.drone.offboard.stop()
                print("-- Offboard mode stopped")
            except Exception as e:
                print(f"-- Warning: Could not stop offboard mode: {e}")
        
        # Give time for cleanup
        await asyncio.sleep(1)
        
        # The MAVSDK System doesn't have an explicit disconnect method,
        # but we can clear our reference to help with cleanup
        self.drone = None
        
        print("-- Mission completed successfully!")
    
    async def _navigate_waypoints_from_csv(self, csv_filename: str) -> None:
        """Navigate through waypoints loaded from a CSV file."""
        with open(csv_filename, newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            n = 0.0
            e = 0.0
            d = 0.0
            
            for row in reader:
                # Save the current row number in case the program is stopped mid-flight
                row_num = reader.line_num
                dn = float(row[0]) - n
                de = float(row[1]) - e
                n = float(row[0])
                e = float(row[1])
                d = float(row[2])

                yaw = math.degrees(math.atan2(de, dn))
                print(f"Waypoint: N={n}m, E={e}m, D={d}m, Yaw={yaw}°")

                await self.drone.offboard.set_position_ned(PositionNedYaw(n, e, d, yaw))
                await self.wait_until_at_waypoint(n, e, d)

                if not self.ready_for_offboard:
                    print(f"Flight interrupted at row {row_num}, N={n}, E={e}, D={d}.")
                    break
    
    async def _return_home_and_land(self) -> None:
        """Return the drone to home position and land."""
        print("-- Returning home")
        await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, -1.0))
        await self.wait_until_at_waypoint(0.0, 0.0, -1.0, 0.5)
        await asyncio.sleep(5)
        print("-- Landing")
        await self.drone.action.land()
        await asyncio.sleep(10)
        print("-- Stopping offboard")
        
        # Cancel offboard control
        try:
            await self.drone.offboard.stop()
        except OffboardError as error:
            print(f"Stopping offboard mode failed with error code: {error._result.result}")

    async def check_who_controls(self) -> None:
        """Monitor who is in control of the drone (Offboard or Manual)."""
        try:
            async for flight_mode in self.drone.telemetry.flight_mode():
                if flight_mode == FlightMode.OFFBOARD:
                    if not self.ready_for_offboard:
                        print("-- Offboard has taken control")
                        self.ready_for_offboard = True
                else:
                    if self.ready_for_offboard:
                        print("-- Offboard has lost control")
                        self.ready_for_offboard = False
        except asyncio.CancelledError:
            print("-- Flight mode monitoring stopped")
            raise

    async def monitor_battery(self) -> None:
        """Monitor the battery level and alert if low."""
        try:
            async for battery in self.drone.telemetry.battery():
                if battery.remaining_percent < 0.2:
                    print(f"Warning: Low battery ({battery.remaining_percent*100:.1f}%)")
                # Initiate RTL on critical battery
                if battery.remaining_percent < 0.1:
                    print("Critical battery level! Initiating Return to Launch (RTL).")
                    await self.drone.action.return_to_launch()
                    await self.wait_until_at_waypoint(0.0, 0.0, 0.0)  # Wait until back at home position
                    await asyncio.sleep(5)  # Stabilize for a few seconds
                    break
                await asyncio.sleep(5)  # Check battery level every 5 seconds
        except asyncio.CancelledError:
            print("-- Battery monitoring stopped")
            raise



    async def wait_until_at_waypoint(
        self, 
        target_north: float, 
        target_east: float, 
        target_down: float, 
        threshold: float = .15
    ) -> Optional[object]:
        """
        Wait until the drone reaches the target waypoint within the specified threshold distance.

        Args:
            target_north: Target North position in meters (NED frame)
            target_east: Target East position in meters (NED frame)
            target_down: Target Down position in meters (NED frame, negative = up)
            threshold: Distance threshold in meters (default: 0.15m)

        Returns:
            The final position when the waypoint is reached, or None if interrupted
        """
        print(f"-- Waiting to reach waypoint: N={target_north}m, E={target_east}m, D={target_down}m (threshold: {threshold}m)")

        while True:
            # Get only the latest telemetry reading
            position = await anext(self.drone.telemetry.position_velocity_ned())
            # Calculate distance to target
            dn = position.position.north_m - target_north
            de = position.position.east_m - target_east
            dd = position.position.down_m - target_down
            distance = (dn**2 + de**2 + dd**2) ** 0.5
            
            if distance < threshold:
                print(f"-- Reached waypoint! Final distance: {distance:.2f}m")
                return position
            if not self.ready_for_offboard:
                break
            await asyncio.sleep(1/50)  # Check every 20ms
        
        return None


def main(
    csv_file: str = "coordinates.csv", 
    system_address: str = "udpin://0.0.0.0:14540"
) -> None:
    """
    Main entry point for the PX4 CSV waypoint navigation script.
    
    Args:
        csv_file: Path to the CSV file containing waypoints
        system_address: Connection address for the drone system
    """
    controller = DroneController(system_address)
    asyncio.run(controller.run_mission(csv_file))


if __name__ == "__main__":
    # Run the module as a standalone script
    main()
