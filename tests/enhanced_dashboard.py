#!/usr/bin/env python3
"""
Enhanced Dashboard with System Checks and Live Data Monitoring
"""

import sys
import os
import asyncio
import time
import json
import random
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment
os.environ['AUTOMOTIVE_LLM_MOCK_MODE'] = 'true'
os.environ['AUTOMOTIVE_LLM_DEBUG'] = 'true'

def create_enhanced_dashboard_html():
    """Create enhanced dashboard HTML with system checks."""
    
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Automotive Analytics Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .system-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
        }
        .status-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        .status-good { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-error { background-color: #F44336; }
        .status-unknown { background-color: #9E9E9E; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 {
            margin-top: 0;
            color: #fff;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-value {
            font-weight: bold;
            color: #4CAF50;
            font-size: 1.1em;
        }
        .live-data {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .btn.danger {
            background: linear-gradient(45deg, #F44336, #d32f2f);
        }
        .last-update {
            font-size: 12px;
            color: #ccc;
            text-align: right;
            margin-top: 10px;
        }
        .data-flow {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
            border-left: 4px solid #4CAF50;
        }
        .alert {
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid rgba(255, 193, 7, 0.5);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .alert.error {
            background: rgba(244, 67, 54, 0.2);
            border-color: rgba(244, 67, 54, 0.5);
        }
        .connection-test {
            display: flex;
            align-items: center;
            padding: 5px 0;
            font-size: 14px;
        }
        .test-result {
            margin-left: 10px;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .test-pass { background-color: rgba(76, 175, 80, 0.3); }
        .test-fail { background-color: rgba(244, 67, 54, 0.3); }
        .test-pending { background-color: rgba(158, 158, 158, 0.3); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Enhanced Automotive Analytics Dashboard</h1>
            <p>Real-time system monitoring with connectivity checks</p>
            <div class="last-update" id="page-last-update">Loading...</div>
        </div>

        <!-- System Status Overview -->
        <div class="system-status">
            <div class="status-card">
                <h4>🌐 API Connection</h4>
                <div id="api-status">
                    <span class="status-indicator status-unknown"></span>
                    <span id="api-status-text">Checking...</span>
                </div>
                <div class="test-result" id="api-test-result">Testing...</div>
            </div>
            
            <div class="status-card">
                <h4>🔌 WebSocket</h4>
                <div id="websocket-status">
                    <span class="status-indicator status-unknown"></span>
                    <span id="websocket-status-text">Connecting...</span>
                </div>
                <div class="test-result" id="websocket-test-result">Testing...</div>
            </div>
            
            <div class="status-card">
                <h4>📊 Data Collection</h4>
                <div id="data-collection-status">
                    <span class="status-indicator status-unknown"></span>
                    <span id="data-collection-text">Checking...</span>
                </div>
                <div class="test-result" id="data-test-result">Testing...</div>
            </div>
            
            <div class="status-card">
                <h4>🎮 Virtual Drive</h4>
                <div id="virtual-drive-status">
                    <span class="status-indicator status-unknown"></span>
                    <span id="virtual-drive-text">Detecting...</span>
                </div>
                <div class="test-result" id="virtual-drive-result">Testing...</div>
            </div>
        </div>

        <!-- Main Dashboard -->
        <div class="dashboard-grid">
            <!-- Live System Diagnostics -->
            <div class="card">
                <h3>🔍 Live System Diagnostics</h3>
                <div class="connection-test">
                    <span>API Status Endpoint:</span>
                    <div class="test-result test-pending" id="test-api-status">Testing...</div>
                </div>
                <div class="connection-test">
                    <span>Alerts Endpoint:</span>
                    <div class="test-result test-pending" id="test-api-alerts">Testing...</div>
                </div>
                <div class="connection-test">
                    <span>Logging Control:</span>
                    <div class="test-result test-pending" id="test-api-logging">Testing...</div>
                </div>
                <div class="connection-test">
                    <span>Data Generation:</span>
                    <div class="test-result test-pending" id="test-data-generation">Testing...</div>
                </div>
                <div class="last-update" id="diagnostics-last-update">Never</div>
            </div>

            <!-- Real-Time Data Flow -->
            <div class="card">
                <h3>📡 Real-Time Data Flow</h3>
                <div class="data-flow" id="data-flow-log">
                    Monitoring data flow...<br>
                </div>
                <div class="metric">
                    <span>Data Points Received:</span>
                    <span class="metric-value" id="data-points-received">0</span>
                </div>
                <div class="metric">
                    <span>Last Data Update:</span>
                    <span class="metric-value" id="last-data-update">Never</span>
                </div>
                <div class="metric">
                    <span>Update Frequency:</span>
                    <span class="metric-value" id="update-frequency">0/min</span>
                </div>
            </div>

            <!-- Performance Summary -->
            <div class="card">
                <h3>🏁 Performance Summary</h3>
                <div class="metric">
                    <span>Active Sessions:</span>
                    <span class="metric-value" id="sessions-count">0</span>
                </div>
                <div class="metric">
                    <span>Total Distance:</span>
                    <span class="metric-value" id="total-distance">0.0 km</span>
                </div>
                <div class="metric">
                    <span>Average Speed:</span>
                    <span class="metric-value" id="avg-speed">0.0 km/h</span>
                </div>
                <div class="metric">
                    <span>Max Engine Temp:</span>
                    <span class="metric-value" id="max-temp">0.0 °C</span>
                </div>
                <div class="last-update" id="performance-last-update">Never</div>
            </div>

            <!-- Logging Status -->
            <div class="card">
                <h3>📝 Logging Status</h3>
                <div class="metric">
                    <span>Logger Status:</span>
                    <span class="metric-value" id="logger-status">Unknown</span>
                </div>
                <div class="metric">
                    <span>Current Session:</span>
                    <span class="metric-value" id="current-session">None</span>
                </div>
                <div class="metric">
                    <span>Data Points:</span>
                    <span class="metric-value" id="session-data-points">0</span>
                </div>
                <div class="metric">
                    <span>Log Level:</span>
                    <span class="metric-value" id="log-level">Unknown</span>
                </div>
                <div style="margin-top: 15px;">
                    <button class="btn" onclick="startLogging()">Start New Session</button>
                    <button class="btn danger" onclick="stopLogging()">Stop Logging</button>
                </div>
                <div class="last-update" id="logging-last-update">Never</div>
            </div>

            <!-- Live Vehicle Data -->
            <div class="card">
                <h3>🚗 Live Vehicle Data</h3>
                <div class="live-data" id="vehicle-data">
                    No vehicle data received yet...<br>
                    Waiting for data from virtual drive test...<br>
                </div>
                <div class="metric">
                    <span>Vehicle Connected:</span>
                    <span class="metric-value" id="vehicle-connected">Unknown</span>
                </div>
                <div class="metric">
                    <span>Data Source:</span>
                    <span class="metric-value" id="data-source">Unknown</span>
                </div>
            </div>

            <!-- Active Alerts -->
            <div class="card">
                <h3>⚠️ Active Alerts</h3>
                <div id="active-alerts">
                    <p>No alerts available</p>
                </div>
                <div class="last-update" id="alerts-last-update">Never</div>
            </div>
        </div>

        <!-- Debug Information -->
        <div class="card">
            <h3>🛠️ Debug Information</h3>
            <div class="live-data" id="debug-log">
                Dashboard initialized...<br>
            </div>
            <button class="btn" onclick="runFullDiagnostic()">Run Full Diagnostic</button>
            <button class="btn" onclick="clearDebugLog()">Clear Debug Log</button>
        </div>
    </div>

    <script>
        let wsConnection = null;
        let dataPointsReceived = 0;
        let lastDataUpdate = null;
        let updateCount = 0;
        let lastMinuteUpdates = 0;
        
        function addDebugLog(message) {
            const debugLog = document.getElementById('debug-log');
            const timestamp = new Date().toLocaleTimeString();
            debugLog.innerHTML += `[${timestamp}] ${message}<br>`;
            debugLog.scrollTop = debugLog.scrollHeight;
        }
        
        function addDataFlowLog(message) {
            const dataFlow = document.getElementById('data-flow-log');
            const timestamp = new Date().toLocaleTimeString();
            dataFlow.innerHTML += `[${timestamp}] ${message}<br>`;
            dataFlow.scrollTop = dataFlow.scrollHeight;
            
            // Keep only last 10 lines
            const lines = dataFlow.innerHTML.split('<br>');
            if (lines.length > 10) {
                dataFlow.innerHTML = lines.slice(-10).join('<br>');
            }
        }
        
        function updateStatus(elementId, status, text) {
            const indicator = document.querySelector(`#${elementId} .status-indicator`);
            const textElement = document.querySelector(`#${elementId}-text`);
            
            indicator.className = `status-indicator status-${status}`;
            if (textElement) textElement.textContent = text;
        }
        
        function updateTestResult(elementId, status, text) {
            const element = document.getElementById(elementId);
            if (element) {
                element.className = `test-result test-${status}`;
                element.textContent = text;
            }
        }
        
        function connectWebSocket() {
            addDebugLog('🔌 Attempting WebSocket connection...');
            
            try {
                wsConnection = new WebSocket('ws://localhost:8080/ws');
                
                wsConnection.onopen = function(event) {
                    addDebugLog('✅ WebSocket connected successfully');
                    updateStatus('websocket-status', 'good', 'Connected');
                    updateTestResult('websocket-test-result', 'pass', 'Connected');
                    addDataFlowLog('WebSocket connection established');
                };
                
                wsConnection.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        addDataFlowLog(`📨 Received: ${data.type || 'unknown'} (${event.data.length} bytes)`);
                        
                        dataPointsReceived++;
                        lastDataUpdate = new Date();
                        updateCount++;
                        
                        document.getElementById('data-points-received').textContent = dataPointsReceived;
                        document.getElementById('last-data-update').textContent = lastDataUpdate.toLocaleTimeString();
                        
                        // Update vehicle data if available
                        if (data.vehicle_data) {
                            updateVehicleData(data.vehicle_data);
                        }
                        
                    } catch (e) {
                        addDataFlowLog(`📨 Raw message: ${event.data.substring(0, 50)}...`);
                    }
                };
                
                wsConnection.onerror = function(error) {
                    addDebugLog('❌ WebSocket error: ' + error);
                    updateStatus('websocket-status', 'error', 'Error');
                    updateTestResult('websocket-test-result', 'fail', 'Connection failed');
                };
                
                wsConnection.onclose = function(event) {
                    addDebugLog('🔌 WebSocket closed, attempting reconnect in 5s...');
                    updateStatus('websocket-status', 'warning', 'Reconnecting...');
                    setTimeout(connectWebSocket, 5000);
                };
                
            } catch (error) {
                addDebugLog('❌ WebSocket connection failed: ' + error);
                updateStatus('websocket-status', 'error', 'Failed');
                updateTestResult('websocket-test-result', 'fail', 'Connection failed');
            }
        }
        
        function updateVehicleData(vehicleData) {
            const vehicleDataElement = document.getElementById('vehicle-data');
            const timestamp = new Date().toLocaleTimeString();
            
            let dataText = `[${timestamp}] Vehicle Update:<br>`;
            for (const [key, value] of Object.entries(vehicleData)) {
                dataText += `  ${key}: ${value}<br>`;
            }
            
            vehicleDataElement.innerHTML = dataText + vehicleDataElement.innerHTML.split('<br>').slice(0, 20).join('<br>');
            
            document.getElementById('vehicle-connected').textContent = 'Yes';
            document.getElementById('data-source').textContent = 'Virtual Drive';
        }
        
        async function testAPIEndpoint(endpoint, elementId) {
            try {
                addDebugLog(`🧪 Testing ${endpoint}...`);
                const response = await fetch(endpoint);
                
                if (response.ok) {
                    const data = await response.json();
                    addDebugLog(`✅ ${endpoint} responded: ${Object.keys(data).length} keys`);
                    updateTestResult(elementId, 'pass', `${response.status} OK`);
                    return data;
                } else {
                    addDebugLog(`❌ ${endpoint} failed: ${response.status}`);
                    updateTestResult(elementId, 'fail', `${response.status} Error`);
                    return null;
                }
            } catch (error) {
                addDebugLog(`❌ ${endpoint} error: ${error.message}`);
                updateTestResult(elementId, 'fail', 'Connection failed');
                return null;
            }
        }
        
        async function updateDashboard() {
            addDataFlowLog('🔄 Updating dashboard data...');
            
            try {
                // Test API status endpoint
                const statusData = await testAPIEndpoint('/api/status', 'test-api-status');
                
                if (statusData) {
                    updateStatus('api-status', 'good', 'Connected');
                    updateTestResult('api-test-result', 'pass', 'Responding');
                    
                    // Update performance summary
                    if (statusData.performance) {
                        document.getElementById('sessions-count').textContent = statusData.performance.total_sessions || 0;
                        document.getElementById('total-distance').textContent = (statusData.performance.total_distance || 0).toFixed(1) + ' km';
                        document.getElementById('avg-speed').textContent = (statusData.performance.avg_speed || 0).toFixed(1) + ' km/h';
                        document.getElementById('max-temp').textContent = (statusData.performance.avg_max_engine_temp || 0).toFixed(1) + ' °C';
                        document.getElementById('performance-last-update').textContent = new Date().toLocaleTimeString();
                    }
                    
                    // Update logging status
                    if (statusData.logging) {
                        const logging = statusData.logging;
                        const loggerStatus = document.getElementById('logger-status');
                        
                        if (logging.logging_active) {
                            loggerStatus.innerHTML = '<span class="status-indicator status-good"></span>Active';
                            updateStatus('data-collection-status', 'good', 'Active');
                        } else {
                            loggerStatus.innerHTML = '<span class="status-indicator status-warning"></span>Standby';
                            updateStatus('data-collection-status', 'warning', 'Standby');
                        }
                        
                        if (logging.current_session) {
                            document.getElementById('current-session').textContent = logging.current_session.session_id || 'None';
                            document.getElementById('session-data-points').textContent = logging.current_session.total_points || 0;
                            
                            // Check if data is being collected
                            const dataPoints = logging.current_session.total_points || 0;
                            if (dataPoints > 0) {
                                updateTestResult('data-test-result', 'pass', `${dataPoints} points`);
                                updateStatus('data-collection-status', 'good', `${dataPoints} points`);
                            } else {
                                updateTestResult('data-test-result', 'fail', 'No data points');
                                updateStatus('data-collection-status', 'warning', 'No data');
                            }
                        }
                        
                        document.getElementById('log-level').textContent = logging.log_level || 'Unknown';
                        document.getElementById('logging-last-update').textContent = new Date().toLocaleTimeString();
                    }
                    
                    addDataFlowLog(`✅ Dashboard updated - Session: ${statusData.logging?.current_session?.session_id || 'None'}`);
                } else {
                    updateStatus('api-status', 'error', 'Failed');
                    updateTestResult('api-test-result', 'fail', 'No response');
                    addDataFlowLog('❌ Failed to update dashboard data');
                }
                
                // Test alerts endpoint
                await testAPIEndpoint('/api/alerts', 'test-api-alerts');
                
                // Update page timestamp
                document.getElementById('page-last-update').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                
                // Calculate update frequency
                lastMinuteUpdates = updateCount;
                document.getElementById('update-frequency').textContent = `${lastMinuteUpdates}/min`;
                
            } catch (error) {
                addDebugLog('❌ Dashboard update failed: ' + error.message);
                updateStatus('api-status', 'error', 'Failed');
                addDataFlowLog('❌ Dashboard update error: ' + error.message);
            }
        }
        
        async function updateAlerts() {
            try {
                const alerts = await testAPIEndpoint('/api/alerts', 'test-api-alerts');
                
                const alertsDiv = document.getElementById('active-alerts');
                if (alerts && alerts.length === 0) {
                    alertsDiv.innerHTML = '<p>No active alerts</p>';
                } else if (alerts && alerts.length > 0) {
                    alertsDiv.innerHTML = alerts.map(alert => 
                        `<div class="alert ${alert.level || 'warning'}">
                            <strong>${(alert.level || 'unknown').toUpperCase()}</strong>: ${alert.message || 'No message'}
                            <br><small>${new Date((alert.timestamp || 0) * 1000).toLocaleString()}</small>
                        </div>`
                    ).join('');
                }
                
                document.getElementById('alerts-last-update').textContent = new Date().toLocaleTimeString();
                
            } catch (error) {
                addDebugLog('❌ Failed to update alerts: ' + error.message);
            }
        }
        
        async function startLogging() {
            try {
                addDebugLog('🔄 Starting new logging session...');
                const response = await fetch('/api/logging/start', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_name: `dashboard_${Date.now()}` })
                });
                
                const result = await response.json();
                if (result.success || response.ok) {
                    addDebugLog(`✅ Logging started: ${result.session_id || 'unknown'}`);
                    addDataFlowLog(`🔄 New logging session: ${result.session_id || 'unknown'}`);
                    updateDashboard();
                } else {
                    addDebugLog('❌ Failed to start logging: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                addDebugLog('❌ Error starting logging: ' + error.message);
            }
        }
        
        async function stopLogging() {
            try {
                addDebugLog('⏹️ Stopping logging session...');
                const response = await fetch('/api/logging/stop', { method: 'POST' });
                const result = await response.json();
                addDebugLog('✅ Logging stopped');
                addDataFlowLog('⏹️ Logging session stopped');
                updateDashboard();
            } catch (error) {
                addDebugLog('❌ Error stopping logging: ' + error.message);
            }
        }
        
        async function runFullDiagnostic() {
            addDebugLog('🔍 Running full system diagnostic...');
            
            // Test all endpoints
            await testAPIEndpoint('/api/status', 'test-api-status');
            await testAPIEndpoint('/api/alerts', 'test-api-alerts');
            
            // Test logging control
            updateTestResult('test-api-logging', 'pending', 'Testing...');
            try {
                const response = await fetch('/api/logging/start', { method: 'POST' });
                if (response.ok) {
                    updateTestResult('test-api-logging', 'pass', 'Working');
                } else {
                    updateTestResult('test-api-logging', 'fail', `Error ${response.status}`);
                }
            } catch (e) {
                updateTestResult('test-api-logging', 'fail', 'Failed');
            }
            
            addDebugLog('✅ Full diagnostic completed');
        }
        
        function clearDebugLog() {
            document.getElementById('debug-log').innerHTML = 'Debug log cleared...<br>';
            document.getElementById('data-flow-log').innerHTML = 'Data flow log cleared...<br>';
        }
        
        // Initialize dashboard
        addDebugLog('🚗 Enhanced Dashboard initializing...');
        connectWebSocket();
        updateDashboard();
        updateAlerts();
        
        // Update dashboard every 5 seconds (more frequent)
        setInterval(updateDashboard, 5000);
        setInterval(updateAlerts, 10000);
        
        // Reset update counter every minute
        setInterval(() => {
            updateCount = 0;
        }, 60000);
        
        addDebugLog('✅ Enhanced Dashboard initialization complete');
        addDataFlowLog('🚗 Dashboard monitoring started');
    </script>
</body>
</html>
'''
    
    return html_content

async def start_enhanced_dashboard():
    """Start the enhanced dashboard with system checks."""
    print("🚗 STARTING ENHANCED DASHBOARD WITH SYSTEM CHECKS")
    print("=" * 70)
    
    try:
        from analytics.dashboard import AnalyticsDashboard
        from analytics.performance_monitor import PerformanceMonitor
        from analytics.data_logger import DataLogger, LoggingConfig
        from interfaces.vehicle import VehicleManager
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        import uvicorn
        
        # Initialize components
        print("🔧 Initializing enhanced dashboard components...")
        vehicle = VehicleManager()
        monitor = PerformanceMonitor(vehicle)
        config = LoggingConfig()
        logger = DataLogger(config, vehicle_manager=vehicle)
        
        await vehicle.initialize()
        await monitor.start_monitoring()
        await logger.start_logging("enhanced_dashboard_session")
        
        print("✅ Components initialized")
        
        # Create enhanced dashboard
        dashboard = AnalyticsDashboard(monitor, logger)
        app = dashboard.app
        
        # Override the main page with enhanced HTML
        enhanced_html = create_enhanced_dashboard_html()
        
        @app.get("/", response_class=HTMLResponse)
        async def enhanced_dashboard_page():
            return enhanced_html
        
        @app.get("/enhanced", response_class=HTMLResponse)
        async def enhanced_dashboard_page_alt():
            return enhanced_html
        
        print("\n🌐 Enhanced Dashboard Features:")
        print("   • Real-time system status indicators")
        print("   • Live connectivity checks")
        print("   • Data flow monitoring")
        print("   • WebSocket connection status")
        print("   • API endpoint testing")
        print("   • Debug logging")
        print("   • Virtual drive detection")
        
        print(f"\n🚀 Starting Enhanced Dashboard Server...")
        print(f"   📊 Main Dashboard: http://localhost:8080")
        print(f"   🔍 Enhanced View: http://localhost:8080/enhanced")
        print(f"   📖 API Docs: http://localhost:8080/docs")
        
        print(f"\n💡 What You'll See:")
        print(f"   🟢 Green indicators = Working correctly")
        print(f"   🟡 Yellow indicators = Warning/Checking")
        print(f"   🔴 Red indicators = Error/Failed")
        print(f"   📡 Real-time data flow monitoring")
        print(f"   🔍 Live system diagnostics")
        
        print(f"\n⚠️ Press Ctrl+C to stop the dashboard")
        print("=" * 70)
        
        # Start the server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8080,
            log_level="info",
            reload=False
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        print(f"❌ Enhanced dashboard failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Main function."""
    print("🚗 ENHANCED AUTOMOTIVE DASHBOARD")
    print("=" * 80)
    print("This enhanced dashboard includes:")
    print("   🔍 Real-time system checks")
    print("   📡 Live data flow monitoring") 
    print("   🔌 WebSocket connection status")
    print("   🧪 API endpoint testing")
    print("   🚗 Virtual drive detection")
    print("   🛠️ Debug information")
    print("=" * 80)
    
    success = await start_enhanced_dashboard()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced dashboard stopped by user")
        sys.exit(0)