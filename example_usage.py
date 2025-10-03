#!/usr/bin/env python3
"""
Example usage of the PX4 CSV Waypoint Navigation Module

This demonstrates how to use the module both programmatically and as a library.
"""

import asyncio
from px4_csv_waypoints_with_mavsdk import DroneController, main


def example_programmatic_usage():
    """Example of using the module programmatically."""
    print("=== Programmatic Usage Example ===")
    
    # Create a controller instance with custom settings
    controller = DroneController(system_address="udpin://0.0.0.0:14540")
    
    # You could run a mission like this:
    # asyncio.run(controller.run_mission("coordinates.csv"))
    
    print(f"Controller created with address: {controller.system_address}")
    print(f"Ready for offboard: {controller.ready_for_offboard}")


def example_direct_usage():
    """Example of using the main function directly."""
    print("\n=== Direct Usage Example ===")
    
    # Use the main function with custom parameters
    # main(csv_file="coordinates.csv", system_address="udpin://0.0.0.0:14540")
    
    print("Main function can be called with custom CSV file and system address")


if __name__ == "__main__":
    print("PX4 CSV Waypoint Navigation Module - Usage Examples")
    print("=" * 50)
    
    example_programmatic_usage()
    example_direct_usage()
    
    print("\n=== Available Functions ===")
    print("- DroneController: Main class for drone control")
    print("- DroneController.run_mission(): Execute waypoint mission from CSV")
    print("- main(): Standalone entry point function")
    
    print("\n=== To run the actual mission ===")
    print("1. As a script: python px4-csv-waypoints-with-mavsdk.py")
    print("2. Programmatically: from px4_csv_waypoints_with_mavsdk import DroneController")
    print("3. With custom params: main('my_waypoints.csv', 'serial:///dev/ttyUSB0')")