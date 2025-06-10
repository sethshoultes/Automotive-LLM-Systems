#!/usr/bin/env python3
"""
Minimal test script for the Automotive LLM System
Tests core functionality without audio dependencies
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that core modules can be imported."""
    print("🔧 Testing core module imports...")
    
    try:
        from config.settings import Settings
        print("✅ Settings module imported successfully")
    except Exception as e:
        print(f"❌ Settings module failed: {e}")
        return False
    
    try:
        from safety.monitor import SafetyMonitor  
        print("✅ Safety Monitor module imported successfully")
    except Exception as e:
        print(f"❌ Safety Monitor module failed: {e}")
        return False
    
    try:
        from interfaces.vehicle import VehicleManager
        print("✅ Vehicle Manager module imported successfully")
    except Exception as e:
        print(f"❌ Vehicle Manager module failed: {e}")
        return False
    
    try:
        from controllers.hvac_controller import HVACController
        print("✅ HVAC Controller module imported successfully")
    except Exception as e:
        print(f"❌ HVAC Controller module failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration system...")
    
    try:
        os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
        from config.settings import Settings
        
        settings = Settings()
        print(f"✅ Configuration loaded successfully")
        print(f"   Mock mode: {settings.mock_mode}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

async def test_safety_system():
    """Test safety monitoring system."""
    print("\n🛡️ Testing safety system...")
    
    try:
        from safety.monitor import SafetyMonitor
        from config.settings import Settings
        
        settings = Settings()
        safety = SafetyMonitor(settings)
        print(f"✅ Safety monitor initialized with {len(safety.safety_rules)} rules")
        
        # Test a sample validation
        result = await safety.validate_command(
            intent_type='climate_control',
            parameter='temperature',
            value=22,
            vehicle_state={
                'engine_rpm': 800,
                'vehicle_speed': 0,
                'engine_temp': 85,
                'oil_pressure': 45
            }
        )
        print(f"✅ Safety validation completed: {result.allowed}")
        print(f"   Safety level: {result.safety_level}")
        
        return True
    except Exception as e:
        print(f"❌ Safety system failed: {e}")
        return False

async def test_vehicle_interface():
    """Test vehicle interface in mock mode."""
    print("\n🚗 Testing vehicle interface...")
    
    try:
        from interfaces.vehicle import VehicleManager
        
        vehicle = VehicleManager()
        print("✅ Vehicle manager initialized")
        
        # Test getting vehicle data
        data = await vehicle.get_vehicle_status()
        print(f"✅ Mock vehicle data retrieved: {len(data)} parameters")
        sample_param = list(data.values())[0] if data else None
        if sample_param:
            print(f"   Sample data: {sample_param.name}={sample_param.value} {sample_param.unit}")
        
        return True
    except Exception as e:
        print(f"❌ Vehicle interface failed: {e}")
        return False

async def test_hvac_controller():
    """Test HVAC controller functionality."""
    print("\n🌡️ Testing HVAC controller...")
    
    try:
        from controllers.hvac_controller import HVACController
        from interfaces.vehicle import VehicleManager
        
        vehicle = VehicleManager()
        hvac = HVACController(vehicle)
        
        print("✅ HVAC controller initialized")
        
        # Test setting temperature
        result = await hvac.set_temperature(22, zone="driver")
        print(f"✅ Temperature set: {result}")
        
        # Test getting status
        status = await hvac.get_status()
        print(f"✅ HVAC status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ HVAC controller failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚗 Automotive LLM System - Basic Functionality Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Module imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Configuration
    if test_configuration():
        tests_passed += 1
    
    # Test 3: Safety system
    if await test_safety_system():
        tests_passed += 1
    
    # Test 4: Vehicle interface
    if await test_vehicle_interface():
        tests_passed += 1
    
    # Test 5: HVAC controller (async)
    if await test_hvac_controller():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Core system is functional.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    # Set mock mode environment
    os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
    os.environ['AUTOMOTIVE_LLM_DEBUG'] = 'true'
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)