# Vehicle Analytics and Performance Monitoring Guide

## Overview

The Automotive LLM System includes a comprehensive analytics and performance monitoring system that tracks, logs, and analyzes vehicle performance data in real-time. This system provides insights into vehicle health, performance trends, and operational efficiency.

## Features

### 📊 **Performance Monitoring**
- **Real-time Data Collection**: Continuous monitoring of engine, thermal, and electrical systems
- **Session Tracking**: Automatic driving session detection and analysis
- **Alert Management**: Multi-level alerts for performance anomalies
- **Trend Analysis**: Historical performance trend analysis

### 📋 **Data Logging**
- **Configurable Logging Levels**: From minimal to diagnostic detail
- **Multiple Export Formats**: CSV, JSON, binary, and SQLite
- **Automatic Compression**: Efficient storage with gzip compression
- **Retention Management**: Automatic cleanup of old log files

### 🌐 **Web Dashboard**
- **Real-time Visualization**: Live performance monitoring dashboard
- **Interactive Controls**: Start/stop logging, export data, manage alerts
- **Performance Summaries**: Historical analysis and reporting
- **WebSocket Updates**: Real-time data streaming

## Getting Started

### 1. Basic Setup

#### Import Analytics Components
```python
from analytics.performance_monitor import PerformanceMonitor
from analytics.data_logger import DataLogger, LoggingConfig, LogLevel
from analytics.dashboard import DashboardManager

# Initialize components
performance_monitor = PerformanceMonitor(vehicle_manager)
data_logger = DataLogger(LoggingConfig(log_level=LogLevel.STANDARD))
dashboard_manager = DashboardManager(performance_monitor, data_logger)
```

#### Start Monitoring
```python
# Start performance monitoring
await performance_monitor.start_monitoring()

# Start data logging
session_id = await data_logger.start_logging("my_session")

# Start web dashboard (optional)
await dashboard_manager.start()
```

### 2. Integration with Main System

Add to your `SystemController` initialization:

```python
# In SystemController.__init__()
self.performance_monitor = PerformanceMonitor(
    vehicle_manager=self.vehicle_manager,
    data_directory="data/performance"
)

self.data_logger = DataLogger(
    config=LoggingConfig(
        log_level=LogLevel.STANDARD,
        collection_interval=5.0,
        auto_export_interval=3600
    ),
    vehicle_manager=self.vehicle_manager
)

# In SystemController.initialize()
await self.performance_monitor.initialize()
await self.performance_monitor.start_monitoring()

# Optional: Start dashboard
if self.settings.system.enable_dashboard:
    self.dashboard_manager = DashboardManager(
        self.performance_monitor, 
        self.data_logger
    )
    asyncio.create_task(self.dashboard_manager.start())
```

## Performance Monitoring

### Automatic Session Detection

The system automatically detects driving sessions:

```python
# Sessions start when vehicle speed > 5 km/h
# Sessions end after 5 minutes of idle time

# Get current session info
if performance_monitor.current_session:
    session = performance_monitor.current_session
    print(f"Session: {session.session_id}")
    print(f"Distance: {session.total_distance:.1f} km")
    print(f"Duration: {session.session_duration/60:.1f} minutes")
```

### Performance Metrics Tracked

#### Engine Performance
- **RPM**: Engine revolutions per minute
- **Temperature**: Coolant temperature monitoring
- **Oil Pressure**: Lubrication system health
- **Throttle Position**: Driver input tracking
- **Load**: Calculated engine load

#### Fuel Economy
- **Instantaneous**: Real-time fuel consumption
- **Average**: Session-based fuel economy
- **Trends**: Long-term efficiency analysis

#### Thermal Management
- **Engine Temperature**: Coolant temperature trends
- **Intake Temperature**: Air temperature monitoring
- **Thermal Efficiency**: Heat management analysis

### Alert System

#### Alert Levels
```python
# Configure alert thresholds
performance_monitor.performance_thresholds = {
    "engine_temp": {"warning": 100.0, "critical": 105.0},
    "oil_pressure": {"warning": 20.0, "critical": 15.0},
    "boost_pressure": {"warning": 15.0, "critical": 18.0}
}

# Get active alerts
alerts = performance_monitor.get_active_alerts()
for alert in alerts:
    print(f"{alert.level.value}: {alert.message}")
```

#### Managing Alerts
```python
# Acknowledge an alert
await performance_monitor.acknowledge_alert(alert_id)

# Resolve an alert
await performance_monitor.resolve_alert(alert_id)
```

### Performance Analysis

#### Get Performance Summary
```python
# Get 30-day performance summary
summary = await performance_monitor.get_performance_summary(days=30)

print(f"Total Sessions: {summary['total_sessions']}")
print(f"Total Distance: {summary['total_distance']:.1f} km")
print(f"Average Fuel Economy: {summary['avg_fuel_economy']:.2f} L/100km")
print(f"Average Engine Temp: {summary['avg_max_engine_temp']:.1f}°C")
```

#### Trend Analysis
```python
# Analyze engine temperature trends
temp_trend = await performance_monitor.get_performance_trends(
    parameter="engine_temp", 
    days=30
)

print(f"Trend Direction: {temp_trend.trend_direction}")
print(f"Trend Strength: {temp_trend.trend_strength:.2f}")
print(f"Average: {temp_trend.avg_value:.1f}°C")
print(f"Range: {temp_trend.min_value:.1f} - {temp_trend.max_value:.1f}°C")
```

### Data Export

#### Export Performance Data
```python
from datetime import datetime, timedelta

# Export last 30 days to JSON
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()

export_path = await performance_monitor.export_performance_data(
    start_date=start_date,
    end_date=end_date,
    format="json"
)

print(f"Data exported to: {export_path}")
```

## Data Logging

### Logging Levels

#### Configure Logging Detail
```python
from analytics.data_logger import LogLevel

# Minimal logging (basic parameters only)
config = LoggingConfig(log_level=LogLevel.MINIMAL)

# Standard logging (common performance metrics)
config = LoggingConfig(log_level=LogLevel.STANDARD)

# Detailed logging (all available parameters)
config = LoggingConfig(log_level=LogLevel.DETAILED)

# Diagnostic logging (maximum detail)
config = LoggingConfig(log_level=LogLevel.DIAGNOSTIC)
```

#### Logging Configuration
```python
config = LoggingConfig(
    log_level=LogLevel.STANDARD,
    collection_interval=1.0,  # seconds
    buffer_size=1000,
    auto_export_interval=3600,  # 1 hour
    compression_enabled=True,
    retention_days=30,
    export_formats=[DataFormat.CSV, DataFormat.JSON]
)
```

### Managing Logging Sessions

#### Start/Stop Logging
```python
# Start a named session
session_id = await data_logger.start_logging("highway_test_drive")

# Change logging level during session
await data_logger.change_log_level(LogLevel.DETAILED)

# Stop logging and get session info
session = await data_logger.stop_logging()
print(f"Logged {session.total_points} data points")
```

#### Export Session Data
```python
# Export specific session
export_path = await data_logger.export_session_data(
    session_id="highway_test_drive",
    format_type=DataFormat.CSV
)
```

### Data Formats

#### CSV Export Example
```csv
timestamp,parameter,value,unit,source,quality
1672531200.0,engine_rpm,2500.0,rpm,obd,1.0
1672531200.0,engine_temp,85.5,°C,obd,1.0
1672531200.0,vehicle_speed,65.0,km/h,obd,1.0
```

#### JSON Export Example
```json
{
  "session_id": "highway_test_drive",
  "export_time": 1672531200.0,
  "log_level": "standard",
  "data_points": [
    {
      "timestamp": 1672531200.0,
      "parameter": "engine_rpm",
      "value": 2500.0,
      "unit": "rpm",
      "source": "obd",
      "quality": 1.0,
      "metadata": {
        "system_type": "engine_performance"
      }
    }
  ]
}
```

### Storage Management

#### Monitor Storage Usage
```python
storage_info = data_logger.get_storage_usage()

print(f"Total Size: {storage_info['total_size_mb']:.1f} MB")
print(f"File Count: {storage_info['file_count']}")
print(f"Compression Savings: {storage_info['compression_savings_mb']:.1f} MB")
```

#### Cleanup Old Files
```python
# Clean up files older than retention period
await data_logger.cleanup_old_files()
```

## Web Dashboard

### Accessing the Dashboard

#### Start Dashboard Server
```python
dashboard_manager = DashboardManager(
    performance_monitor, 
    data_logger,
    dashboard_config={
        "host": "0.0.0.0",
        "port": 8080
    }
)

await dashboard_manager.start()
print(f"Dashboard available at: {dashboard_manager.get_dashboard_url()}")
```

#### Dashboard Features
- **Real-time Status**: System health and current performance
- **Performance Summary**: Historical data analysis
- **Active Alerts**: Current performance alerts
- **Logging Controls**: Start/stop data logging
- **Export Functions**: Download data in various formats

### API Endpoints

#### System Status
```bash
curl http://localhost:8080/api/status
```

#### Performance Summary
```bash
curl http://localhost:8080/api/performance/summary?days=7
```

#### Export Data
```bash
curl -X POST http://localhost:8080/api/export/performance?days=30&format=json
```

#### Start/Stop Logging
```bash
# Start logging
curl -X POST http://localhost:8080/api/logging/start

# Stop logging
curl -X POST http://localhost:8080/api/logging/stop
```

## Voice Commands for Analytics

Add analytics voice commands to your system:

```python
# In LLM controller, add analytics intents
ANALYTICS_COMMANDS = {
    "show performance summary": "get_performance_summary",
    "start data logging": "start_logging",
    "stop data logging": "stop_logging",
    "export performance data": "export_data",
    "check active alerts": "get_alerts"
}

# Example voice command handlers
async def handle_analytics_command(self, intent):
    if intent.action == "get_performance_summary":
        summary = await self.performance_monitor.get_performance_summary(days=7)
        return f"This week: {summary['total_sessions']} sessions, {summary['total_distance']:.1f} km driven"
    
    elif intent.action == "start_logging":
        session_id = await self.data_logger.start_logging()
        return f"Data logging started: {session_id}"
    
    elif intent.action == "get_alerts":
        alerts = self.performance_monitor.get_active_alerts()
        if alerts:
            return f"You have {len(alerts)} active alerts"
        return "No active performance alerts"
```

### Voice Commands Examples
```
"Hey Car, show me this week's performance summary"
"Start data logging for this trip"
"Do I have any performance alerts?"
"Export my driving data from last month"
"What's my average fuel economy this week?"
```

## Advanced Analytics

### Custom Metrics

#### Add Custom Performance Calculations
```python
# Extend PerformanceMonitor for custom metrics
class CustomPerformanceMonitor(PerformanceMonitor):
    async def _calculate_custom_metrics(self, data, timestamp, session_id):
        # Power-to-weight ratio calculation
        if "engine_rpm" in data and "throttle_pos" in data:
            rpm = float(data["engine_rpm"].value)
            throttle = float(data["throttle_pos"].value)
            
            # Simplified power calculation
            estimated_power = (rpm * throttle) / 100.0
            
            metric = PerformanceMetric(
                timestamp=timestamp,
                metric_type=MetricType.ENGINE_PERFORMANCE,
                parameter_name="estimated_power",
                value=estimated_power,
                unit="hp",
                source="calculated",
                session_id=session_id
            )
            
            self.metrics_cache.append(metric)
```

### Integration with External Systems

#### Export to External Analytics
```python
def on_data_export(file_path: str, format_type):
    """Callback for external system integration."""
    if format_type == DataFormat.JSON:
        # Send to cloud analytics service
        send_to_analytics_service(file_path)
    
    elif format_type == DataFormat.CSV:
        # Import into external database
        import_to_database(file_path)

data_logger.add_export_callback(on_data_export)
```

#### Real-time Streaming
```python
# Stream data to external systems
async def stream_to_external_system(self):
    while self.monitoring_active:
        recent_metrics = self.get_recent_metrics(60)  # Last minute
        
        for metric in recent_metrics:
            await external_api.send_metric(asdict(metric))
        
        await asyncio.sleep(30)  # Stream every 30 seconds
```

## Troubleshooting

### Common Issues

#### 1. High Storage Usage
```python
# Monitor storage and set limits
storage_info = data_logger.get_storage_usage()
if storage_info['total_size_mb'] > 1000:  # 1GB limit
    # Reduce logging level or increase cleanup frequency
    await data_logger.change_log_level(LogLevel.MINIMAL)
    await data_logger.cleanup_old_files()
```

#### 2. Performance Impact
```python
# Reduce collection frequency for better performance
config = LoggingConfig(
    collection_interval=10.0,  # Reduce from 1.0 to 10.0 seconds
    buffer_size=500,           # Reduce buffer size
    auto_export_interval=7200  # Export less frequently
)
```

#### 3. Dashboard Not Accessible
```bash
# Check if FastAPI is installed
pip install fastapi uvicorn

# Check firewall settings
sudo ufw allow 8080

# Check if port is in use
netstat -tulpn | grep 8080
```

### Performance Optimization

#### Database Optimization
```python
# Regular database maintenance
await performance_monitor._optimize_database()

# Archive old data
await performance_monitor._archive_old_data(days=90)
```

#### Memory Management
```python
# Monitor memory usage
import psutil

memory_usage = psutil.virtual_memory().percent
if memory_usage > 80:
    # Reduce buffer sizes
    data_logger.config.buffer_size = 500
    performance_monitor.cache_size = 500
```

## Configuration Examples

### Production Configuration
```python
# config/analytics.yaml
analytics:
  performance_monitor:
    collection_interval: 5.0
    monitoring_interval: 1.0
    cache_size: 1000
    
  data_logger:
    log_level: "standard"
    collection_interval: 5.0
    buffer_size: 1000
    auto_export_interval: 3600
    compression_enabled: true
    retention_days: 30
    export_formats: ["json", "csv"]
    
  dashboard:
    enabled: true
    host: "0.0.0.0"
    port: 8080
    update_interval: 10.0
```

### Development Configuration
```python
# Minimal impact for development
analytics:
  performance_monitor:
    collection_interval: 10.0
    cache_size: 100
    
  data_logger:
    log_level: "minimal"
    collection_interval: 10.0
    buffer_size: 100
    auto_export_interval: 7200
    compression_enabled: false
    retention_days: 7
    
  dashboard:
    enabled: false
```

The analytics system provides comprehensive insight into your vehicle's performance while maintaining the safety and reliability standards of the Automotive LLM System. Use these features to optimize performance, track maintenance needs, and ensure safe operation of your classic car's modern systems.