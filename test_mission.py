#!/usr/bin/env python3
"""
Test script to actually run the drone mission
Make sure PX4 SITL is running first!
"""

import asyncio
from px4_csv_waypoints_with_mavsdk import DroneController, main


async def test_with_connection():
    """Test the drone controller with actual connection."""
    print("=== Testing Drone Connection ===")
    
    controller = DroneController(system_address="udpin://0.0.0.0:14540")
    
    print("Attempting to run mission...")
    print("Make sure PX4 SITL is running!")
    print("You'll need to switch to OFFBOARD mode in QGroundControl")
    
    try:
        await controller.run_mission("coordinatesfast.csv")
        print("\n=== Test Complete! ===")
    except KeyboardInterrupt:
        print("\n=== Test Interrupted by User (Ctrl+C) ===")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("1. PX4 SITL is running (make px4_sitl_default gz_x500)")
        print("2. QGroundControl is connected")
        print("3. Switch to OFFBOARD mode when prompted")


def test_main_function():
    """Test using the main function."""
    print("\n=== Testing Main Function ===")
    
    try:
        main("coordinatesfar.csv", "udpin://0.0.0.0:14540")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Choose test method:")
    print("1. Test with async (recommended)")
    print("2. Test with main function")
    print("Press Enter for default (1)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    # Default to option 1 if nothing entered
    if choice == "" or choice == "1":
        print("Running async test...")
        asyncio.run(test_with_connection())
    elif choice == "2":
        print("Running main function test...")
        test_main_function()
    else:
        print(f"Invalid choice: '{choice}'. Please enter 1 or 2.")
        print("Defaulting to option 1...")
        asyncio.run(test_with_connection())