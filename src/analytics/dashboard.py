"""
Analytics Dashboard - Web-based dashboard for vehicle performance monitoring
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("FastAPI not available - dashboard will be disabled")

from analytics.performance_monitor import PerformanceMonitor, PerformanceTrend
from analytics.data_logger import DataLogger, LogLevel, DataFormat


class WebSocketManager:
    """Manages WebSocket connections for real-time data."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


class AnalyticsDashboard:
    """Web-based analytics dashboard for vehicle performance monitoring."""
    
    def __init__(self, 
                 performance_monitor: PerformanceMonitor,
                 data_logger: DataLogger,
                 host: str = "0.0.0.0",
                 port: int = 8080):
        
        self.performance_monitor = performance_monitor
        self.data_logger = data_logger
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        if not FASTAPI_AVAILABLE:
            self.logger.error("FastAPI not available - dashboard cannot be started")
            self.app = None
            return
        
        # Create FastAPI app
        self.app = FastAPI(title="Automotive Analytics Dashboard", version="1.0.0")
        
        # CORS middleware for web access
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WebSocket manager for real-time updates
        self.websocket_manager = WebSocketManager()
        
        # Dashboard state
        self.dashboard_active = False
        self.update_task: Optional[asyncio.Task] = None
        self.update_interval = 5.0  # seconds
        
        # Setup routes
        self._setup_routes()
        self._setup_static_files()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Serve the main dashboard page."""
            return self._get_dashboard_html()
        
        @self.app.get("/api/status")
        async def get_system_status():
            """Get current system status."""
            try:
                perf_summary = await self.performance_monitor.get_performance_summary(days=1)
                logging_status = self.data_logger.get_logging_status()
                storage_usage = self.data_logger.get_storage_usage()
                
                return {
                    "timestamp": time.time(),
                    "performance": perf_summary,
                    "logging": logging_status,
                    "storage": storage_usage,
                    "dashboard_active": self.dashboard_active
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/performance/summary")
        async def get_performance_summary(days: int = 7):
            """Get performance summary for specified days."""
            try:
                summary = await self.performance_monitor.get_performance_summary(days)
                return summary
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/performance/trends/{parameter}")
        async def get_performance_trends(parameter: str, days: int = 30):
            """Get performance trends for a parameter."""
            try:
                trends = await self.performance_monitor.get_performance_trends(parameter, days)
                return asdict(trends)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/alerts")
        async def get_active_alerts():
            """Get current active alerts."""
            try:
                alerts = self.performance_monitor.get_active_alerts()
                return [asdict(alert) for alert in alerts]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(alert_id: str):
            """Acknowledge an alert."""
            try:
                success = await self.performance_monitor.acknowledge_alert(alert_id)
                return {"success": success}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str):
            """Resolve an alert."""
            try:
                success = await self.performance_monitor.resolve_alert(alert_id)
                return {"success": success}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/logging/start")
        async def start_logging(session_name: Optional[str] = None):
            """Start data logging session."""
            try:
                session_id = await self.data_logger.start_logging(session_name)
                return {"session_id": session_id, "success": bool(session_id)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/logging/stop")
        async def stop_logging():
            """Stop current logging session."""
            try:
                session = await self.data_logger.stop_logging()
                return {"session": asdict(session) if session else None}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/logging/level")
        async def change_log_level(level: str):
            """Change logging level."""
            try:
                log_level = LogLevel(level)
                await self.data_logger.change_log_level(log_level)
                return {"success": True, "new_level": level}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid log level")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/export/performance")
        async def export_performance_data(days: int = 30, format: str = "json"):
            """Export performance data."""
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                export_path = await self.performance_monitor.export_performance_data(
                    start_date, end_date, format
                )
                
                return {"export_path": export_path, "success": bool(export_path)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/export/logs")
        async def export_log_data(session_id: str, format: str = "json"):
            """Export log data for a session."""
            try:
                data_format = DataFormat(format)
                export_path = await self.data_logger.export_session_data(
                    session_id, format_type=data_format
                )
                
                return {"export_path": export_path, "success": bool(export_path)}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid format")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time data."""
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and handle incoming messages
                    data = await websocket.receive_text()
                    # Echo back for now (could handle commands in the future)
                    await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
    
    def _setup_static_files(self):
        """Setup static file serving for dashboard assets."""
        # In a full implementation, would serve CSS, JS, and other assets
        pass
    
    def _get_dashboard_html(self) -> str:
        """Generate the main dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automotive Analytics Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #333;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-good { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-critical { background-color: #F44336; }
        .alert {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
        }
        .alert.critical {
            background-color: #f8d7da;
            border-color: #f5c6cb;
        }
        .btn {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background-color: #5a67d8;
        }
        .btn.danger {
            background-color: #F44336;
        }
        .btn.danger:hover {
            background-color: #d32f2f;
        }
        #realtime-data {
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Automotive Analytics Dashboard</h1>
            <p>Real-time vehicle performance monitoring and analytics</p>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <h3>System Status</h3>
                <div id="system-status">
                    <div class="metric">
                        <span>Dashboard</span>
                        <span class="metric-value">
                            <span class="status-indicator status-good"></span>
                            Online
                        </span>
                    </div>
                    <div class="metric">
                        <span>Performance Monitor</span>
                        <span class="metric-value" id="perf-status">
                            <span class="status-indicator status-good"></span>
                            Active
                        </span>
                    </div>
                    <div class="metric">
                        <span>Data Logger</span>
                        <span class="metric-value" id="logger-status">
                            <span class="status-indicator status-warning"></span>
                            Standby
                        </span>
                    </div>
                </div>
                <button class="btn" onclick="startLogging()">Start Logging</button>
                <button class="btn danger" onclick="stopLogging()">Stop Logging</button>
            </div>

            <div class="card">
                <h3>Performance Summary (24h)</h3>
                <div id="performance-summary">
                    <div class="metric">
                        <span>Sessions</span>
                        <span class="metric-value" id="sessions-count">-</span>
                    </div>
                    <div class="metric">
                        <span>Distance</span>
                        <span class="metric-value" id="total-distance">- km</span>
                    </div>
                    <div class="metric">
                        <span>Avg Speed</span>
                        <span class="metric-value" id="avg-speed">- km/h</span>
                    </div>
                    <div class="metric">
                        <span>Max Engine Temp</span>
                        <span class="metric-value" id="max-temp">- °C</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>Active Alerts</h3>
                <div id="active-alerts">
                    <p>No active alerts</p>
                </div>
            </div>

            <div class="card">
                <h3>Storage Usage</h3>
                <div id="storage-usage">
                    <div class="metric">
                        <span>Total Size</span>
                        <span class="metric-value" id="storage-size">- MB</span>
                    </div>
                    <div class="metric">
                        <span>File Count</span>
                        <span class="metric-value" id="file-count">-</span>
                    </div>
                    <div class="metric">
                        <span>Compression Savings</span>
                        <span class="metric-value" id="compression-savings">- MB</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Real-time Data Stream</h3>
            <div id="realtime-data">
                Connecting to real-time data stream...
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let reconnectInterval = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                console.log('WebSocket connected');
                document.getElementById('realtime-data').innerHTML = 'Connected to real-time data stream\\n';
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onmessage = function(event) {
                const data = event.data;
                const realtimeDiv = document.getElementById('realtime-data');
                realtimeDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + data + '\\n';
                realtimeDiv.scrollTop = realtimeDiv.scrollHeight;
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket disconnected');
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update performance summary
                if (data.performance) {
                    document.getElementById('sessions-count').textContent = data.performance.total_sessions || 0;
                    document.getElementById('total-distance').textContent = (data.performance.total_distance || 0).toFixed(1) + ' km';
                    document.getElementById('avg-speed').textContent = (data.performance.avg_speed || 0).toFixed(1) + ' km/h';
                    document.getElementById('max-temp').textContent = (data.performance.avg_max_engine_temp || 0).toFixed(1) + ' °C';
                }
                
                // Update storage usage
                if (data.storage) {
                    document.getElementById('storage-size').textContent = (data.storage.total_size_mb || 0).toFixed(1) + ' MB';
                    document.getElementById('file-count').textContent = data.storage.file_count || 0;
                    document.getElementById('compression-savings').textContent = (data.storage.compression_savings_mb || 0).toFixed(1) + ' MB';
                }
                
                // Update logging status
                if (data.logging) {
                    const loggerStatus = document.getElementById('logger-status');
                    if (data.logging.logging_active) {
                        loggerStatus.innerHTML = '<span class="status-indicator status-good"></span>Active';
                    } else {
                        loggerStatus.innerHTML = '<span class="status-indicator status-warning"></span>Standby';
                    }
                }
                
            } catch (error) {
                console.error('Failed to update dashboard:', error);
            }
        }

        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const alerts = await response.json();
                
                const alertsDiv = document.getElementById('active-alerts');
                if (alerts.length === 0) {
                    alertsDiv.innerHTML = '<p>No active alerts</p>';
                } else {
                    alertsDiv.innerHTML = alerts.map(alert => 
                        `<div class="alert ${alert.level}">
                            <strong>${alert.level.toUpperCase()}</strong>: ${alert.message}
                            <br><small>${new Date(alert.timestamp * 1000).toLocaleString()}</small>
                        </div>`
                    ).join('');
                }
                
            } catch (error) {
                console.error('Failed to update alerts:', error);
            }
        }

        async function startLogging() {
            try {
                const response = await fetch('/api/logging/start', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    alert('Logging started: ' + result.session_id);
                    updateDashboard();
                } else {
                    alert('Failed to start logging');
                }
            } catch (error) {
                alert('Error starting logging: ' + error.message);
            }
        }

        async function stopLogging() {
            try {
                const response = await fetch('/api/logging/stop', { method: 'POST' });
                const result = await response.json();
                alert('Logging stopped');
                updateDashboard();
            } catch (error) {
                alert('Error stopping logging: ' + error.message);
            }
        }

        // Initialize dashboard
        connectWebSocket();
        updateDashboard();
        updateAlerts();

        // Update dashboard every 10 seconds
        setInterval(updateDashboard, 10000);
        setInterval(updateAlerts, 15000);
    </script>
</body>
</html>
        """
    
    async def start_dashboard(self) -> None:
        """Start the analytics dashboard server."""
        if not FASTAPI_AVAILABLE or not self.app:
            self.logger.error("Cannot start dashboard - FastAPI not available")
            return
        
        try:
            self.dashboard_active = True
            self.update_task = asyncio.create_task(self._real_time_update_loop())
            
            self.logger.info(f"🌐 Starting analytics dashboard on http://{self.host}:{self.port}")
            
            # Start FastAPI server
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"Dashboard startup error: {e}")
            self.dashboard_active = False
    
    async def stop_dashboard(self) -> None:
        """Stop the analytics dashboard."""
        self.dashboard_active = False
        
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🛑 Analytics dashboard stopped")
    
    async def _real_time_update_loop(self) -> None:
        """Send real-time updates to connected WebSocket clients."""
        while self.dashboard_active:
            try:
                # Get current system status
                status_data = {
                    "timestamp": time.time(),
                    "type": "status_update",
                    "data": {
                        "active_connections": len(self.websocket_manager.active_connections),
                        "dashboard_active": self.dashboard_active
                    }
                }
                
                # Broadcast to all connected clients
                if self.websocket_manager.active_connections:
                    await self.websocket_manager.broadcast(json.dumps(status_data))
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Real-time update error: {e}")
                await asyncio.sleep(self.update_interval)
    
    def get_dashboard_url(self) -> str:
        """Get the dashboard URL."""
        return f"http://{self.host}:{self.port}"
    
    async def send_alert_notification(self, alert_data: Dict[str, Any]) -> None:
        """Send alert notification to dashboard clients."""
        try:
            notification = {
                "timestamp": time.time(),
                "type": "alert",
                "data": alert_data
            }
            
            await self.websocket_manager.broadcast(json.dumps(notification))
            
        except Exception as e:
            self.logger.error(f"Alert notification error: {e}")
    
    async def send_performance_update(self, performance_data: Dict[str, Any]) -> None:
        """Send performance data update to clients."""
        try:
            update = {
                "timestamp": time.time(),
                "type": "performance_update",
                "data": performance_data
            }
            
            await self.websocket_manager.broadcast(json.dumps(update))
            
        except Exception as e:
            self.logger.error(f"Performance update error: {e}")


class DashboardManager:
    """Manager for integrating dashboard with analytics systems."""
    
    def __init__(self, 
                 performance_monitor: PerformanceMonitor,
                 data_logger: DataLogger,
                 dashboard_config: Optional[Dict[str, Any]] = None):
        
        self.performance_monitor = performance_monitor
        self.data_logger = data_logger
        self.config = dashboard_config or {}
        self.logger = logging.getLogger(__name__)
        
        # Create dashboard
        self.dashboard = AnalyticsDashboard(
            performance_monitor=performance_monitor,
            data_logger=data_logger,
            host=self.config.get("host", "0.0.0.0"),
            port=self.config.get("port", 8080)
        )
        
        # Setup callbacks for real-time updates
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup callbacks for real-time dashboard updates."""
        
        def on_data_export(file_path: str, format_type):
            """Callback for data export events."""
            asyncio.create_task(self.dashboard.send_performance_update({
                "event": "data_exported",
                "file_path": file_path,
                "format": format_type.value
            }))
        
        # Add export callback to data logger
        self.data_logger.add_export_callback(on_data_export)
    
    async def start(self) -> None:
        """Start the dashboard manager."""
        try:
            self.logger.info("🚀 Starting Dashboard Manager...")
            
            # Start dashboard server
            await self.dashboard.start_dashboard()
            
        except Exception as e:
            self.logger.error(f"Dashboard manager start error: {e}")
    
    async def stop(self) -> None:
        """Stop the dashboard manager."""
        try:
            await self.dashboard.stop_dashboard()
            self.logger.info("✅ Dashboard Manager stopped")
            
        except Exception as e:
            self.logger.error(f"Dashboard manager stop error: {e}")
    
    def get_dashboard_url(self) -> str:
        """Get the dashboard URL."""
        return self.dashboard.get_dashboard_url()