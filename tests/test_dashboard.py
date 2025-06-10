#!/usr/bin/env python3
"""
Test script for the Analytics Dashboard
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_analytics_components():
    """Test analytics system components."""
    print("📊 Testing Analytics Components...")
    
    try:
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger
        from interfaces.vehicle import VehicleManager
        from config.settings import Settings
        
        settings = Settings()
        vehicle = VehicleManager()
        
        # Test Performance Monitor
        monitor = PerformanceMonitor(vehicle)
        print("✅ Performance Monitor initialized")
        
        # Test Data Logger
        from analytics.data_logger import LoggingConfig, LogLevel
        log_config = LoggingConfig()
        logger = DataLogger(log_config)
        print("✅ Data Logger initialized")
        
        # Test starting a logging session
        session_id = await logger.start_logging("test_session")
        print(f"✅ Logging session started: {session_id}")
        
        # Stop logging session
        await logger.stop_logging()
        print("✅ Logging session stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics components failed: {e}")
        return False

async def test_dashboard_server():
    """Test dashboard web server."""
    print("\n🌐 Testing Dashboard Server...")
    
    try:
        from analytics.dashboard import AnalyticsDashboard
        from interfaces.vehicle import VehicleManager
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger
        
        vehicle = VehicleManager()
        monitor = PerformanceMonitor(vehicle)
        from analytics.data_logger import LoggingConfig
        log_config = LoggingConfig()
        logger = DataLogger(log_config)
        
        # Create the dashboard
        dashboard = AnalyticsDashboard(monitor, logger)
        print("✅ Dashboard created successfully")
        
        # Test that we can import uvicorn for serving
        import uvicorn
        print("✅ Uvicorn server available")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard server failed: {e}")
        return False

async def test_mock_llm():
    """Test LLM controller in mock mode."""
    print("\n🧠 Testing LLM Controller...")
    
    try:
        from controllers.llm_controller import LLMController
        from config.settings import Settings
        
        settings = Settings()
        llm = LLMController(settings)
        print("✅ LLM Controller initialized")
        
        # Test command processing
        test_command = "Set temperature to 22 degrees"
        result = await llm.process_command(test_command)
        print(f"✅ Command processed: {result.intent} - {result.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Controller failed: {e}")
        return False

async def main():
    """Run dashboard and LLM tests."""
    print("🚗 Automotive LLM System - Dashboard & LLM Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Analytics components
    if await test_analytics_components():
        tests_passed += 1
    
    # Test 2: Dashboard server
    if await test_dashboard_server():
        tests_passed += 1
    
    # Test 3: LLM controller
    if await test_mock_llm():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 Dashboard and LLM components are functional!")
        print("\n💡 To test the web dashboard:")
        print("   export AUTOMOTIVE_LLM_MOCK_MODE=true")
        print("   export AUTOMOTIVE_LLM_ENABLE_DASHBOARD=true")
        print("   python src/analytics/dashboard.py")
        print("   # Then open http://localhost:8080")
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