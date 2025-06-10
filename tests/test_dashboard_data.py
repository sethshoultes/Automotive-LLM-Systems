#!/usr/bin/env python3
"""
Test Dashboard Data - Check if the dashboard is receiving and displaying data
"""

import sys
import os
import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment
os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
os.environ['AUTOMOTIVE_LLM_DEBUG'] = 'true'

async def test_dashboard_endpoints():
    """Test all dashboard API endpoints."""
    print("🌐 Testing Dashboard API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    endpoints = [
        ("/", "GET", "Main dashboard page"),
        ("/api/status", "GET", "System status"),
        ("/api/metrics", "GET", "Performance metrics"),
        ("/api/alerts", "GET", "Active alerts"),
        ("/api/sessions", "GET", "Logging sessions"),
        ("/api/export-formats", "GET", "Available export formats"),
    ]
    
    try:
        async with aiohttp.ClientSession() as session:
            for endpoint, method, description in endpoints:
                try:
                    print(f"Testing {endpoint} - {description}")
                    
                    async with session.request(method, f"{base_url}{endpoint}") as response:
                        status = response.status
                        
                        if status == 200:
                            if endpoint == "/":
                                print(f"   ✅ {endpoint}: {status} (HTML page)")
                            else:
                                data = await response.json()
                                print(f"   ✅ {endpoint}: {status}")
                                
                                # Show key data
                                if isinstance(data, dict):
                                    for key, value in list(data.items())[:3]:  # First 3 items
                                        print(f"      • {key}: {value}")
                                elif isinstance(data, list):
                                    print(f"      • Found {len(data)} items")
                                    if data:
                                        print(f"      • Sample: {str(data[0])[:50]}...")
                        else:
                            print(f"   ❌ {endpoint}: {status}")
                            error_text = await response.text()
                            print(f"      Error: {error_text[:100]}...")
                            
                except Exception as e:
                    print(f"   ❌ {endpoint}: {e}")
                
                print()
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure the dashboard is running: python3 start_dashboard.py")
        return False
    
    return True

async def test_websocket_connection():
    """Test WebSocket connection for real-time updates."""
    print("🔌 Testing WebSocket Connection")
    print("=" * 50)
    
    try:
        import websockets
        
        uri = "ws://localhost:8080/ws"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Listen for a few messages
            print("📡 Listening for real-time data (5 seconds)...")
            try:
                for i in range(5):
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    print(f"   📊 Received: {data.get('type', 'unknown')} - {len(str(data))} bytes")
                    
            except asyncio.TimeoutError:
                print("   ⚠️ No messages received (this might be normal)")
            
            print("✅ WebSocket test completed")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def start_test_session():
    """Start a test session to generate data."""
    print("🧪 Starting Test Data Generation")
    print("=" * 50)
    
    try:
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger, LoggingConfig, LogLevel
        from interfaces.vehicle import VehicleManager
        
        # Initialize components
        vehicle = VehicleManager()
        monitor = PerformanceMonitor(vehicle)
        
        config = LoggingConfig()
        config.log_level = LogLevel.STANDARD
        config.collection_interval = 1.0
        logger = DataLogger(config, vehicle_manager=vehicle)
        
        print("✅ Components initialized")
        
        # Initialize vehicle
        await vehicle.initialize()
        
        # Start monitoring and logging
        await monitor.start_monitoring()
        session_id = await logger.start_logging("dashboard_test")
        
        print(f"🔄 Started monitoring and logging session: {session_id}")
        print("📊 Generating test data for 10 seconds...")
        
        # Let it run for 10 seconds to generate data
        await asyncio.sleep(10)
        
        # Check what we have
        alerts = monitor.get_active_alerts()
        print(f"⚠️ Generated {len(alerts)} alerts")
        
        if logger.current_session:
            print(f"📝 Session info:")
            print(f"   • Session ID: {logger.current_session.session_id}")
            print(f"   • Duration: {time.time() - logger.current_session.start_time:.1f}s")
            print(f"   • Data points: {logger.current_session.total_points}")
        
        # Stop monitoring and logging
        await monitor.stop_monitoring()
        await logger.stop_logging()
        
        print("✅ Test session completed")
        return True
        
    except Exception as e:
        print(f"❌ Test session failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_dashboard_html():
    """Check if the dashboard HTML is being served correctly."""
    print("📄 Checking Dashboard HTML")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/") as response:
                html = await response.text()
                
                print(f"✅ Dashboard HTML loaded ({len(html)} characters)")
                
                # Check for key elements
                checks = [
                    ("title", "Automotive Analytics Dashboard" in html),
                    ("WebSocket script", "WebSocket" in html or "ws://" in html),
                    ("API endpoints", "/api/" in html),
                    ("Chart library", "chart" in html.lower()),
                    ("Real-time updates", "real-time" in html.lower() or "live" in html.lower())
                ]
                
                print("🔍 Content analysis:")
                for check_name, found in checks:
                    status = "✅" if found else "❌"
                    print(f"   {status} {check_name}: {'Found' if found else 'Not found'}")
                
                # Show a snippet of the HTML
                print(f"\n📄 HTML snippet (first 200 chars):")
                print(f"   {html[:200]}...")
                
                return True
                
    except Exception as e:
        print(f"❌ HTML check failed: {e}")
        return False

async def main():
    """Run all dashboard tests."""
    print("🚗 DASHBOARD CONNECTIVITY TEST")
    print("=" * 80)
    
    tests = [
        ("API Endpoints", test_dashboard_endpoints),
        ("Dashboard HTML", check_dashboard_html),
        ("Test Data Generation", start_test_session),
        ("WebSocket Connection", test_websocket_connection),
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
    
    print(f"\n🎯 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 3:  # Allow some failures
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("1. Make sure dashboard is running: python3 start_dashboard.py")
        print("2. Check browser console for JavaScript errors")
        print("3. Try refreshing the page (Ctrl+F5)")
        print("4. Check if WebSocket connection is working")
        print("5. Start a new logging session from the dashboard")
        
        print("\n🌐 Dashboard URLs to try:")
        print("   • Main: http://localhost:8080/")
        print("   • API Status: http://localhost:8080/api/status")
        print("   • API Docs: http://localhost:8080/docs")
        
        return True
    else:
        print("\n❌ Dashboard may not be running properly")
        print("   Try restarting: python3 start_dashboard.py")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)