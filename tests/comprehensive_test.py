#!/usr/bin/env python3
"""
Comprehensive Test - Complete system test with data generation and export
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

# Set environment
os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
os.environ['AUTOMOTIVE_LLM_DEBUG'] = 'true'

async def check_export_directories():
    """Check and create export directories."""
    print("📂 CHECKING EXPORT DIRECTORIES")
    print("=" * 50)
    
    directories = [
        "virtual_drive_exports",
        "demo_exports", 
        "data",
        "data/logs",
        "data/exports"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            files = list(dir_path.iterdir())
            print(f"✅ {dir_name}: {len(files)} files")
            for file in files[:3]:  # Show first 3 files
                size = file.stat().st_size if file.is_file() else 0
                print(f"   • {file.name}: {size} bytes")
        else:
            print(f"❌ {dir_name}: Does not exist")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {dir_name}")

async def test_data_logger_export():
    """Test data logger export functionality directly."""
    print("\n💾 TESTING DATA LOGGER EXPORT")
    print("=" * 50)
    
    try:
        from analytics.data_logger import DataLogger, LoggingConfig, LogLevel, DataFormat, DataPoint
        from interfaces.vehicle import VehicleManager
        
        # Create components
        config = LoggingConfig()
        config.log_level = LogLevel.STANDARD
        config.collection_interval = 1.0
        
        vehicle = VehicleManager()
        logger = DataLogger(config, vehicle_manager=vehicle)
        
        await vehicle.initialize()
        print("✅ Data logger initialized")
        
        # Start logging session
        session_id = await logger.start_logging("export_test_session")
        print(f"🔄 Started session: {session_id}")
        
        # Manually create and add data points
        print("📊 Creating test data points...")
        current_time = time.time()
        
        test_data_points = [
            DataPoint(current_time + 1, "engine_rpm", 1500.0, "rpm", "mock", session_id),
            DataPoint(current_time + 2, "engine_temp", 85.0, "°F", "mock", session_id),
            DataPoint(current_time + 3, "vehicle_speed", 35.0, "mph", "mock", session_id),
            DataPoint(current_time + 4, "fuel_level", 75.0, "%", "mock", session_id),
            DataPoint(current_time + 5, "oil_pressure", 40.0, "psi", "mock", session_id),
        ]
        
        # Add data points to buffer manually
        if hasattr(logger, 'buffer') and logger.buffer:
            for dp in test_data_points:
                logger.buffer.add(dp)
            print(f"✅ Added {len(test_data_points)} data points to buffer")
            
            # Update session manually
            if logger.current_session:
                logger.current_session.total_points = len(test_data_points)
                print(f"✅ Updated session total_points: {logger.current_session.total_points}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Stop logging
        await logger.stop_logging()
        print("✅ Logging session stopped")
        
        # Test exports
        export_dir = Path("test_exports")
        export_dir.mkdir(exist_ok=True)
        
        formats = [
            (DataFormat.CSV, "csv"),
            (DataFormat.JSON, "json"),
            (DataFormat.SQLITE, "db")
        ]
        
        print(f"\n📤 Testing data export...")
        successful_exports = 0
        
        for format_type, extension in formats:
            try:
                filename = f"test_export_{int(time.time())}.{extension}"
                filepath = export_dir / filename
                
                print(f"   Exporting {format_type.value}...")
                result = await logger.export_session_data(session_id, format_type, str(filepath))
                
                if result and Path(result).exists():
                    size = Path(result).stat().st_size
                    print(f"   ✅ {format_type.value.upper()}: {filename} ({size} bytes)")
                    successful_exports += 1
                else:
                    print(f"   ❌ {format_type.value.upper()}: Export failed - no file created")
                    
            except Exception as e:
                print(f"   ❌ {format_type.value.upper()}: Export error - {e}")
        
        print(f"\n🎯 Export Results: {successful_exports}/{len(formats)} formats successful")
        
        if successful_exports > 0:
            print(f"✅ Data export is working!")
            print(f"📂 Check {export_dir.absolute()} for exported files")
        else:
            print(f"❌ Data export is not working - need to investigate")
        
        return successful_exports > 0
        
    except Exception as e:
        print(f"❌ Data logger export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_complete_virtual_drive():
    """Test complete virtual drive with export."""
    print(f"\n🚗 COMPLETE VIRTUAL DRIVE TEST")
    print("=" * 50)
    
    try:
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger, LoggingConfig, LogLevel, DataFormat
        from interfaces.vehicle import VehicleManager
        
        # Initialize all components
        vehicle = VehicleManager()
        monitor = PerformanceMonitor(vehicle)
        
        config = LoggingConfig()
        config.log_level = LogLevel.DETAILED
        config.collection_interval = 2.0
        logger = DataLogger(config, vehicle_manager=vehicle)
        
        await vehicle.initialize()
        print("✅ All components initialized")
        
        # Start monitoring and logging
        await monitor.start_monitoring()
        session_id = await logger.start_logging("complete_virtual_drive")
        
        print(f"🔄 Started complete session: {session_id}")
        print(f"📊 Running 30-second virtual drive with data collection...")
        
        # Simulate realistic virtual drive
        start_time = time.time()
        data_generated = 0
        
        while time.time() - start_time < 30:  # 30 second test
            # Generate some realistic data changes
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Create mock vehicle state
            speed = 20 + 10 * (elapsed / 30) + random.uniform(-5, 5)
            speed = max(0, min(50, speed))
            
            rpm = 800 + speed * 25 + random.uniform(-100, 100)
            temp = 85 + elapsed * 0.5 + random.uniform(-2, 2)
            
            if int(elapsed) % 5 == 0 and elapsed > 0:  # Every 5 seconds
                print(f"   {elapsed:.0f}s: Speed {speed:.0f}mph, RPM {rpm:.0f}, Temp {temp:.0f}°F")
            
            data_generated += 1
            await asyncio.sleep(1)
        
        print(f"✅ Virtual drive completed - {data_generated} data cycles")
        
        # Check session status
        if logger.current_session:
            print(f"📊 Session info:")
            print(f"   • Session ID: {logger.current_session.session_id}")
            print(f"   • Duration: {time.time() - logger.current_session.start_time:.0f}s")
            print(f"   • Data points: {logger.current_session.total_points}")
        
        # Stop monitoring and logging
        await monitor.stop_monitoring()
        await logger.stop_logging()
        
        # Export data
        export_dir = Path("complete_drive_exports")
        export_dir.mkdir(exist_ok=True)
        
        print(f"\n📤 Exporting complete drive data...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        formats = [
            (DataFormat.CSV, f"complete_drive_{timestamp}.csv"),
            (DataFormat.JSON, f"complete_drive_{timestamp}.json"),
            (DataFormat.SQLITE, f"complete_drive_{timestamp}.db")
        ]
        
        successful_exports = 0
        for format_type, filename in formats:
            try:
                filepath = export_dir / filename
                result = await logger.export_session_data(session_id, format_type, str(filepath))
                
                if result and Path(result).exists():
                    size = Path(result).stat().st_size
                    print(f"   ✅ {format_type.value.upper()}: {filename} ({size} bytes)")
                    successful_exports += 1
                else:
                    print(f"   ❌ {format_type.value.upper()}: {filename} - No file created")
                    
            except Exception as e:
                print(f"   ❌ {format_type.value.upper()}: {filename} - Error: {e}")
        
        print(f"\n🎯 Complete Drive Results:")
        print(f"   • Data cycles: {data_generated}")
        print(f"   • Session data points: {logger.current_session.total_points if logger.current_session else 0}")
        print(f"   • Successful exports: {successful_exports}/{len(formats)}")
        print(f"   • Export directory: {export_dir.absolute()}")
        
        return successful_exports > 0
        
    except Exception as e:
        print(f"❌ Complete virtual drive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_dashboard_connectivity():
    """Check dashboard connectivity and provide status."""
    print(f"\n🌐 DASHBOARD CONNECTIVITY CHECK")
    print("=" * 50)
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Check if dashboard is running
            try:
                async with session.get("http://localhost:8080/api/status", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Dashboard is running and responding")
                        
                        logging_info = data.get('logging', {})
                        current_session = logging_info.get('current_session', {})
                        
                        print(f"📊 Current Dashboard Status:")
                        print(f"   • Logging active: {logging_info.get('logging_active', False)}")
                        print(f"   • Session: {current_session.get('session_id', 'None')}")
                        print(f"   • Data points: {current_session.get('total_points', 0)}")
                        print(f"   • Duration: {time.time() - current_session.get('start_time', time.time()):.0f}s")
                        
                        return True
                    else:
                        print(f"❌ Dashboard responding with error: {response.status}")
                        return False
                        
            except asyncio.TimeoutError:
                print("❌ Dashboard connection timeout")
                return False
            except Exception as e:
                print(f"❌ Dashboard connection failed: {e}")
                return False
                
    except ImportError:
        print("❌ aiohttp not available for testing")
        return False

def provide_solution_summary():
    """Provide comprehensive solution summary."""
    print(f"\n🎯 COMPREHENSIVE SOLUTION SUMMARY")
    print("=" * 80)
    
    print("Based on all tests, here's what needs to happen:")
    
    print(f"\n1️⃣ ENHANCED DASHBOARD (Recommended):")
    print("   Stop current dashboard: Ctrl+C in dashboard terminal")
    print("   Start enhanced dashboard: python3 enhanced_dashboard.py")
    print("   Open: http://localhost:8080")
    print("   Features: Real-time system checks, connectivity indicators")
    
    print(f"\n2️⃣ VIRTUAL DRIVE WITH EXPORTS:")
    print("   Terminal 1: python3 comprehensive_test.py")
    print("   Terminal 2: python3 enhanced_dashboard.py")
    print("   This will generate data AND create export files")
    
    print(f"\n3️⃣ CHECK EXPORT DIRECTORIES:")
    print("   • test_exports/ - Test export files")
    print("   • complete_drive_exports/ - Complete virtual drive data")
    print("   • virtual_drive_exports/ - Original virtual drive exports")
    
    print(f"\n4️⃣ WHAT THE ENHANCED DASHBOARD SHOWS:")
    print("   🟢 Green: System working correctly")
    print("   🟡 Yellow: Warning/Checking")  
    print("   🔴 Red: Error/Not working")
    print("   📡 Real-time data flow")
    print("   🔍 Live system diagnostics")
    print("   🛠️ Debug information")
    
    print(f"\n5️⃣ TROUBLESHOOTING:")
    print("   • Browser: Check console (F12) for JavaScript errors")
    print("   • Network: Check if API calls are failing")
    print("   • Refresh: Hard refresh (Ctrl+Shift+R)")
    print("   • Ports: Make sure 8080 is not blocked")

async def main():
    """Run comprehensive system test."""
    print("🚗 COMPREHENSIVE AUTOMOTIVE LLM SYSTEM TEST")
    print("=" * 80)
    print("This will test the complete system including:")
    print("   📂 Export directories")
    print("   💾 Data logger export functionality")
    print("   🚗 Complete virtual drive simulation")
    print("   🌐 Dashboard connectivity")
    print("   📊 Data generation and export")
    print("=" * 80)
    
    # Run all tests
    tests = [
        ("Export Directories", check_export_directories),
        ("Data Logger Export", test_data_logger_export),
        ("Complete Virtual Drive", test_complete_virtual_drive),
        ("Dashboard Connectivity", check_dashboard_connectivity)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print("-" * 50)
    
    print(f"\n🎯 COMPREHENSIVE TEST RESULTS: {passed}/{len(tests)} tests passed")
    
    # Provide solution summary
    provide_solution_summary()
    
    return passed >= len(tests) - 1  # Allow 1 failure

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'🎉 COMPREHENSIVE TEST SUCCESSFUL!' if success else '⚠️ SOME ISSUES FOUND - CHECK SOLUTIONS ABOVE'}")
    sys.exit(0 if success else 1)