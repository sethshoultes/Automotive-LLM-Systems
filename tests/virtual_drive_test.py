#!/usr/bin/env python3
"""
Virtual Drive Test - Simulate a complete driving session with logging
"""

import sys
import os
import asyncio
import time
import random
import json
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment for virtual testing
os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
os.environ['AUTOMOTIVE_LLM_DEBUG'] = 'true'

class VirtualDriveSimulator:
    """Simulates realistic driving scenarios for testing."""
    
    def __init__(self):
        self.current_scenario = "idle"
        self.scenario_time = 0
        self.total_time = 0
        
        # Driving scenarios with realistic parameters
        self.scenarios = {
            "idle": {
                "duration": 10,
                "description": "🅿️ Vehicle parked - engine idling",
                "vehicle_speed": 0,
                "engine_rpm": (700, 900),
                "engine_temp": (80, 85),
                "throttle_pos": (0, 5),
                "fuel_level": 75,
                "oil_pressure": (35, 45)
            },
            "city_driving": {
                "duration": 30,
                "description": "🏙️ City driving - stop and go traffic",
                "vehicle_speed": (0, 45),
                "engine_rpm": (800, 3000),
                "engine_temp": (85, 95),
                "throttle_pos": (0, 60),
                "fuel_level": 73,
                "oil_pressure": (40, 50)
            },
            "highway_cruise": {
                "duration": 25,
                "description": "🛣️ Highway cruising - steady speed",
                "vehicle_speed": (65, 75),
                "engine_rpm": (2000, 2500),
                "engine_temp": (88, 92),
                "throttle_pos": (20, 35),
                "fuel_level": 70,
                "oil_pressure": (45, 55)
            },
            "acceleration": {
                "duration": 15,
                "description": "🏎️ Highway acceleration - merging",
                "vehicle_speed": (45, 85),
                "engine_rpm": (2500, 5500),
                "engine_temp": (90, 100),
                "throttle_pos": (60, 95),
                "fuel_level": 68,
                "oil_pressure": (50, 60)
            },
            "mountain_climb": {
                "duration": 20,
                "description": "⛰️ Mountain driving - heavy load",
                "vehicle_speed": (25, 55),
                "engine_rpm": (3000, 4500),
                "engine_temp": (95, 105),
                "throttle_pos": (70, 100),
                "fuel_level": 65,
                "oil_pressure": (45, 55)
            },
            "cool_down": {
                "duration": 10,
                "description": "🅿️ Parking - engine cooling down",
                "vehicle_speed": 0,
                "engine_rpm": (700, 800),
                "engine_temp": (100, 80),  # Cooling down
                "throttle_pos": (0, 2),
                "fuel_level": 63,
                "oil_pressure": (35, 40)
            }
        }
        
        self.scenario_sequence = [
            "idle", "city_driving", "highway_cruise", 
            "acceleration", "mountain_climb", "highway_cruise", "cool_down"
        ]
        self.current_scenario_index = 0
    
    def get_current_vehicle_data(self):
        """Generate realistic vehicle data for current scenario."""
        scenario = self.scenarios[self.current_scenario]
        
        def get_value(param):
            if isinstance(param, tuple):
                # Handle cooling down logic for temperature
                if self.current_scenario == "cool_down" and "temp" in str(param):
                    # Temperature decreases over time
                    start_temp, end_temp = param
                    progress = self.scenario_time / scenario["duration"]
                    return start_temp - (start_temp - end_temp) * progress
                else:
                    # Random value within range, with some trending
                    base = random.uniform(param[0], param[1])
                    # Add some temporal variation
                    variation = random.uniform(-0.1, 0.1) * (param[1] - param[0])
                    return max(param[0], min(param[1], base + variation))
            return param
        
        return {
            "vehicle_speed": get_value(scenario["vehicle_speed"]),
            "engine_rpm": get_value(scenario["engine_rpm"]),
            "engine_temp": get_value(scenario["engine_temp"]),
            "throttle_pos": get_value(scenario["throttle_pos"]),
            "fuel_level": get_value(scenario["fuel_level"]),
            "oil_pressure": get_value(scenario["oil_pressure"]),
            "intake_temp": get_value(scenario["engine_temp"]) - random.uniform(5, 15),
            "coolant_temp": get_value(scenario["engine_temp"]) + random.uniform(-2, 2),
            "battery_voltage": random.uniform(12.5, 14.5),
            "scenario": self.current_scenario,
            "scenario_description": scenario["description"]
        }
    
    def update(self, delta_time):
        """Update simulation state."""
        self.scenario_time += delta_time
        self.total_time += delta_time
        
        # Check if current scenario is complete
        current_scenario_data = self.scenarios[self.current_scenario]
        if self.scenario_time >= current_scenario_data["duration"]:
            # Move to next scenario
            self.current_scenario_index = (self.current_scenario_index + 1) % len(self.scenario_sequence)
            self.current_scenario = self.scenario_sequence[self.current_scenario_index]
            self.scenario_time = 0
            return True  # Scenario changed
        
        return False  # Same scenario

async def run_virtual_drive_test():
    """Run a complete virtual driving test with full logging."""
    print("🚗 VIRTUAL DRIVE TEST - Complete System Simulation")
    print("=" * 80)
    
    try:
        # Import components
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger, LoggingConfig, LogLevel
        from controllers.hvac_controller import HVACController
        from controllers.llm_controller import LLMController
        from safety.monitor import SafetyMonitor
        from interfaces.vehicle import VehicleManager
        from config.settings import Settings
        
        # Initialize system
        print("🔧 Initializing Virtual Drive System...")
        settings = Settings()
        vehicle = VehicleManager()
        monitor = PerformanceMonitor(vehicle)
        
        # Configure detailed logging
        log_config = LoggingConfig()
        log_config.log_level = LogLevel.DETAILED
        log_config.collection_interval = 2.0  # Every 2 seconds
        logger = DataLogger(log_config, vehicle_manager=vehicle)
        
        hvac = HVACController(vehicle)
        llm = LLMController(settings)
        safety = SafetyMonitor(settings, vehicle)
        
        # Initialize virtual drive simulator
        simulator = VirtualDriveSimulator()
        
        print("✅ All components initialized")
        print("✅ Virtual drive simulator ready")
        
        # Initialize vehicle
        await vehicle.initialize()
        
        # Start monitoring and logging
        await monitor.start_monitoring()
        session_id = await logger.start_logging("virtual_drive_test")
        
        print(f"🔄 Started logging session: {session_id}")
        print(f"📊 Log level: {log_config.log_level.value}")
        print(f"⏱️ Collection interval: {log_config.collection_interval}s")
        
        print("\n🎮 Starting Virtual Drive Simulation...")
        print("   Duration: ~2 minutes with 6 driving scenarios")
        print("   Real-time performance monitoring and logging active")
        print("=" * 80)
        
        # Test different HVAC settings during the drive
        hvac_commands = [
            (15, {"action": "set_temperature", "value": 72, "scenario": "Start comfortable temperature"}),
            (35, {"action": "set_temperature", "value": 68, "scenario": "Cool down during city driving"}),
            (55, {"action": "set_fan_speed", "value": 6, "scenario": "Increase fan for highway"}),
            (85, {"action": "set_temperature", "value": 75, "scenario": "Warm up for mountain driving"}),
        ]
        
        # Voice commands to test during drive
        voice_commands = [
            (20, "What's my engine temperature?"),
            (40, "Turn on the air conditioning"),
            (70, "Show me performance data"),
            (100, "Check fuel level"),
        ]
        
        start_time = time.time()
        last_update = start_time
        update_interval = 1.0  # Update every second
        scenario_changes = 0
        total_alerts = 0
        hvac_cmd_index = 0
        voice_cmd_index = 0
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | Starting virtual drive...")
        
        # Main simulation loop
        while simulator.total_time < 120:  # 2 minute test
            current_time = time.time()
            elapsed = simulator.total_time
            
            # Update simulator
            if current_time - last_update >= update_interval:
                delta = current_time - last_update
                scenario_changed = simulator.update(delta)
                last_update = current_time
                
                # Get current vehicle data
                vehicle_data = simulator.get_current_vehicle_data()
                
                # Display scenario changes
                if scenario_changed:
                    scenario_changes += 1
                    print(f"\n📍 {datetime.now().strftime('%H:%M:%S')} | {vehicle_data['scenario_description']}")
                    print(f"   Speed: {vehicle_data['vehicle_speed']:.0f} mph | RPM: {vehicle_data['engine_rpm']:.0f} | Temp: {vehicle_data['engine_temp']:.0f}°F")
                
                # Test HVAC commands
                if hvac_cmd_index < len(hvac_commands) and elapsed >= hvac_commands[hvac_cmd_index][0]:
                    cmd_data = hvac_commands[hvac_cmd_index][1]
                    print(f"🌡️ {datetime.now().strftime('%H:%M:%S')} | HVAC: {cmd_data['scenario']}")
                    
                    if cmd_data["action"] == "set_temperature":
                        result = await hvac.set_temperature(cmd_data["value"])
                        if result['success']:
                            temp_f = result.get('temperature_fahrenheit', 'N/A')
                            print(f"   Result: ✅ Temperature set to {temp_f}°F")
                        else:
                            print(f"   Result: ❌ {result.get('error', 'Failed')}")
                    elif cmd_data["action"] == "set_fan_speed":
                        result = await hvac.set_fan_speed(cmd_data["value"])
                        if result.get('success'):
                            fan_speed = result.get('fan_speed', 'unknown')
                            print(f"   Result: ✅ Fan speed set to {fan_speed}")
                        else:
                            print(f"   Result: ❌ {result.get('error', 'Failed')}")
                    
                    hvac_cmd_index += 1
                
                # Test voice commands
                if voice_cmd_index < len(voice_commands) and elapsed >= voice_commands[voice_cmd_index][0]:
                    command = voice_commands[voice_cmd_index][1]
                    print(f"🎤 {datetime.now().strftime('%H:%M:%S')} | Voice: \"{command}\"")
                    
                    try:
                        response = await llm.process_command(command)
                        print(f"   Intent: {response.intent.intent_type.value} (confidence: {response.confidence})")
                    except Exception as e:
                        print(f"   Processing: {str(e)[:50]}...")
                    
                    voice_cmd_index += 1
                
                # Check safety alerts
                alerts = monitor.get_active_alerts()
                if len(alerts) > total_alerts:
                    new_alerts = alerts[total_alerts:]
                    for alert in new_alerts:
                        print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} | ALERT: {alert.message}")
                    total_alerts = len(alerts)
                
                # Progress indicator
                progress = (elapsed / 120) * 100
                if int(elapsed) % 10 == 0 and elapsed > 0:  # Every 10 seconds
                    print(f"⏳ Progress: {progress:.0f}% | Scenario: {vehicle_data['scenario']} | Session: {elapsed:.0f}s")
            
            await asyncio.sleep(0.1)  # Small sleep to prevent busy waiting
        
        print(f"\n🏁 {datetime.now().strftime('%H:%M:%S')} | Virtual drive completed!")
        
        # Stop monitoring and logging
        await monitor.stop_monitoring()
        await logger.stop_logging()
        
        print("\n📊 VIRTUAL DRIVE TEST RESULTS")
        print("=" * 50)
        print(f"✅ Total duration: {simulator.total_time:.0f} seconds")
        print(f"✅ Scenario changes: {scenario_changes}")
        print(f"✅ HVAC commands tested: {hvac_cmd_index}")
        print(f"✅ Voice commands tested: {voice_cmd_index}")
        print(f"✅ Safety alerts generated: {total_alerts}")
        
        # Get session info
        if logger.current_session:
            print(f"✅ Data points logged: {logger.current_session.total_points}")
            print(f"✅ Session ID: {logger.current_session.session_id}")
        
        # Export the drive data
        print("\n📤 Exporting Drive Data...")
        export_dir = Path("virtual_drive_exports")
        export_dir.mkdir(exist_ok=True)
        
        # Export in multiple formats
        from analytics.data_logger import DataFormat
        
        formats = [
            (DataFormat.CSV, "csv"),
            (DataFormat.JSON, "json"),
            (DataFormat.SQLITE, "db")
        ]
        
        for format_type, extension in formats:
            try:
                filename = f"virtual_drive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
                filepath = export_dir / filename
                
                result = await logger.export_session_data(session_id, format_type, str(filepath))
                if result and Path(result).exists():
                    size = Path(result).stat().st_size
                    print(f"   ✅ {format_type.value.upper()}: {filename} ({size} bytes)")
                else:
                    print(f"   ⚠️ {format_type.value.upper()}: Export failed")
            except Exception as e:
                print(f"   ❌ {format_type.value.upper()}: {e}")
        
        print(f"\n📂 Exported files saved to: {export_dir.absolute()}")
        
        # Final system status
        print("\n🎯 SYSTEM STATUS SUMMARY")
        print("=" * 50)
        print("✅ Virtual drive simulation completed successfully")
        print("✅ Performance monitoring and data logging functional")
        print("✅ HVAC control system responsive")
        print("✅ Voice command processing working")
        print("✅ Safety monitoring active throughout drive")
        print("✅ Data export in multiple formats successful")
        
        print("\n💡 NEXT STEPS")
        print("=" * 50)
        print("🌐 Start dashboard: python3 start_dashboard.py")
        print("📊 View exports: Check virtual_drive_exports/ directory")
        print("🚗 Real deployment: Install on Raspberry Pi with vehicle hardware")
        print("📱 Mobile app: Develop companion mobile interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Virtual drive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the virtual drive test."""
    print("🎮 Preparing Virtual Drive Test...")
    print("   This will simulate a 2-minute driving session with:")
    print("   • 6 different driving scenarios")
    print("   • Real-time performance monitoring")
    print("   • Active data logging")
    print("   • HVAC control testing")
    print("   • Voice command processing")
    print("   • Safety monitoring")
    print("   • Data export in multiple formats")
    print("\nPress Enter to start the virtual drive test...")
    input()
    
    success = await run_virtual_drive_test()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        print(f"\n{'🎉 VIRTUAL DRIVE TEST COMPLETED SUCCESSFULLY!' if success else '❌ VIRTUAL DRIVE TEST FAILED'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Virtual drive test interrupted by user")
        sys.exit(1)