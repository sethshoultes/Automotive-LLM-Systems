"""
Performance Monitor - Vehicle analytics and performance tracking system
"""

import asyncio
import logging
import time
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import sqlite3

from interfaces.vehicle import VehicleManager, VehicleParameter


class MetricType(Enum):
    """Types of metrics being tracked."""
    ENGINE_PERFORMANCE = "engine_performance"
    FUEL_ECONOMY = "fuel_economy"
    THERMAL_MANAGEMENT = "thermal_management"
    ELECTRICAL_SYSTEM = "electrical_system"
    DRIVETRAIN = "drivetrain"
    EMISSIONS = "emissions"
    SYSTEM_HEALTH = "system_health"


class AlertLevel(Enum):
    """Alert levels for performance issues."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Individual performance metric data point."""
    timestamp: float
    metric_type: MetricType
    parameter_name: str
    value: float
    unit: str
    source: str
    vehicle_speed: Optional[float] = None
    engine_load: Optional[float] = None
    ambient_temp: Optional[float] = None
    session_id: Optional[str] = None


@dataclass
class PerformanceSession:
    """Driving session with aggregated metrics."""
    session_id: str
    start_time: float
    end_time: Optional[float]
    total_distance: float
    total_fuel_used: float
    max_speed: float
    avg_speed: float
    max_engine_temp: float
    avg_engine_temp: float
    max_rpm: float
    avg_rpm: float
    fuel_economy: float
    session_duration: float
    idle_time: float
    driving_time: float


@dataclass
class PerformanceAlert:
    """Performance monitoring alert."""
    alert_id: str
    timestamp: float
    level: AlertLevel
    metric_type: MetricType
    parameter: str
    current_value: float
    threshold_value: float
    message: str
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class PerformanceTrend:
    """Performance trend analysis over time."""
    parameter: str
    time_period: str  # "daily", "weekly", "monthly"
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0.0 to 1.0
    avg_value: float
    min_value: float
    max_value: float
    std_deviation: float
    data_points: int


class PerformanceMonitor:
    """Comprehensive vehicle performance monitoring and analytics system."""
    
    def __init__(self, 
                 vehicle_manager: VehicleManager,
                 data_directory: str = "data",
                 collection_interval: float = 5.0):
        
        self.vehicle_manager = vehicle_manager
        self.data_directory = Path(data_directory)
        self.collection_interval = collection_interval
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        self.data_directory.mkdir(exist_ok=True)
        
        # Database setup
        self.db_path = self.data_directory / "performance.db"
        self.setup_database()
        
        # Monitoring state
        self.monitoring_active = False
        self.current_session: Optional[PerformanceSession] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.performance_thresholds = {
            "engine_temp": {"warning": 100.0, "critical": 105.0},
            "oil_pressure": {"warning": 20.0, "critical": 15.0},
            "engine_rpm": {"warning": 6000.0, "critical": 6500.0},
            "boost_pressure": {"warning": 15.0, "critical": 18.0},
            "fuel_pressure": {"warning": 300.0, "critical": 250.0},
            "battery_voltage": {"warning": 12.0, "critical": 11.5}
        }
        
        # Analytics cache
        self.metrics_cache: List[PerformanceMetric] = []
        self.cache_size = 1000
        self.active_alerts: List[PerformanceAlert] = []
        
        # Session tracking
        self.session_start_speed_threshold = 5.0  # km/h
        self.session_end_idle_time = 300.0  # 5 minutes
        self.last_activity_time = time.time()
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "total_distance": 0.0,
            "total_fuel_used": 0.0,
            "monitoring_hours": 0.0,
            "alerts_generated": 0,
            "data_points_collected": 0
        }
    
    def setup_database(self) -> None:
        """Initialize SQLite database for performance data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        metric_type TEXT NOT NULL,
                        parameter_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT NOT NULL,
                        source TEXT NOT NULL,
                        vehicle_speed REAL,
                        engine_load REAL,
                        ambient_temp REAL,
                        session_id TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """)
                
                # Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time REAL NOT NULL,
                        end_time REAL,
                        total_distance REAL DEFAULT 0.0,
                        total_fuel_used REAL DEFAULT 0.0,
                        max_speed REAL DEFAULT 0.0,
                        avg_speed REAL DEFAULT 0.0,
                        max_engine_temp REAL DEFAULT 0.0,
                        avg_engine_temp REAL DEFAULT 0.0,
                        max_rpm REAL DEFAULT 0.0,
                        avg_rpm REAL DEFAULT 0.0,
                        fuel_economy REAL DEFAULT 0.0,
                        session_duration REAL DEFAULT 0.0,
                        idle_time REAL DEFAULT 0.0,
                        driving_time REAL DEFAULT 0.0
                    )
                """)
                
                # Alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id TEXT PRIMARY KEY,
                        timestamp REAL NOT NULL,
                        level TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        parameter TEXT NOT NULL,
                        current_value REAL NOT NULL,
                        threshold_value REAL NOT NULL,
                        message TEXT NOT NULL,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_parameter ON performance_metrics(parameter_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
                
                conn.commit()
                self.logger.info("✅ Performance database initialized")
                
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            raise
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("📊 Performance monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # End current session if active
        if self.current_session:
            await self._end_session()
        
        self.logger.info("⏹️ Performance monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main performance monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect performance data
                await self._collect_performance_data()
                
                # Check for alerts
                await self._check_performance_alerts()
                
                # Manage sessions
                await self._manage_sessions()
                
                # Periodic database flush
                if len(self.metrics_cache) >= self.cache_size:
                    await self._flush_metrics_to_db()
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_performance_data(self) -> None:
        """Collect performance data from vehicle systems."""
        try:
            current_time = time.time()
            session_id = self.current_session.session_id if self.current_session else None
            
            # Core engine parameters
            engine_params = [
                "engine_rpm", "engine_temp", "oil_pressure", 
                "throttle_pos", "maf_rate", "fuel_pressure"
            ]
            
            # Vehicle dynamics
            vehicle_params = ["vehicle_speed"]
            
            # Performance parameters (if available)
            performance_params = ["boost_pressure", "intake_temp"]
            
            # Collect all available parameters
            all_params = engine_params + vehicle_params + performance_params
            
            collected_data = {}
            for param in all_params:
                try:
                    vehicle_param = await self.vehicle_manager.get_parameter(param)
                    if vehicle_param:
                        collected_data[param] = vehicle_param
                        
                        # Create performance metric
                        metric = PerformanceMetric(
                            timestamp=current_time,
                            metric_type=self._get_metric_type(param),
                            parameter_name=param,
                            value=float(vehicle_param.value),
                            unit=vehicle_param.unit,
                            source=vehicle_param.source,
                            vehicle_speed=collected_data.get("vehicle_speed", {}).get("value"),
                            session_id=session_id
                        )
                        
                        self.metrics_cache.append(metric)
                        self.stats["data_points_collected"] += 1
                        
                except Exception as e:
                    self.logger.debug(f"Could not collect {param}: {e}")
            
            # Calculate derived metrics
            await self._calculate_derived_metrics(collected_data, current_time, session_id)
            
        except Exception as e:
            self.logger.error(f"Data collection error: {e}")
    
    def _get_metric_type(self, parameter: str) -> MetricType:
        """Determine metric type for a parameter."""
        if parameter in ["engine_rpm", "engine_temp", "oil_pressure", "throttle_pos"]:
            return MetricType.ENGINE_PERFORMANCE
        elif parameter in ["maf_rate", "fuel_pressure"]:
            return MetricType.FUEL_ECONOMY
        elif parameter in ["boost_pressure", "intake_temp"]:
            return MetricType.ENGINE_PERFORMANCE
        elif parameter in ["battery_voltage", "alternator_output"]:
            return MetricType.ELECTRICAL_SYSTEM
        else:
            return MetricType.SYSTEM_HEALTH
    
    async def _calculate_derived_metrics(self, 
                                       data: Dict[str, Any], 
                                       timestamp: float, 
                                       session_id: Optional[str]) -> None:
        """Calculate derived performance metrics."""
        try:
            # Fuel economy calculation (requires speed and fuel flow)
            if "vehicle_speed" in data and "maf_rate" in data:
                speed_kmh = float(data["vehicle_speed"].value)
                maf_gs = float(data["maf_rate"].value)
                
                if speed_kmh > 0 and maf_gs > 0:
                    # Simplified fuel economy calculation
                    # Actual calculation would depend on engine specifics
                    fuel_economy = speed_kmh / (maf_gs * 0.1)  # Simplified
                    
                    metric = PerformanceMetric(
                        timestamp=timestamp,
                        metric_type=MetricType.FUEL_ECONOMY,
                        parameter_name="instantaneous_fuel_economy",
                        value=fuel_economy,
                        unit="km/l",
                        source="calculated",
                        vehicle_speed=speed_kmh,
                        session_id=session_id
                    )
                    self.metrics_cache.append(metric)
            
            # Engine load calculation
            if "throttle_pos" in data and "engine_rpm" in data:
                throttle_pct = float(data["throttle_pos"].value)
                rpm = float(data["engine_rpm"].value)
                
                # Simplified engine load calculation
                engine_load = (throttle_pct * rpm) / 100.0
                
                metric = PerformanceMetric(
                    timestamp=timestamp,
                    metric_type=MetricType.ENGINE_PERFORMANCE,
                    parameter_name="calculated_engine_load",
                    value=engine_load,
                    unit="load_units",
                    source="calculated",
                    session_id=session_id
                )
                self.metrics_cache.append(metric)
                
        except Exception as e:
            self.logger.error(f"Derived metrics calculation error: {e}")
    
    async def _check_performance_alerts(self) -> None:
        """Check for performance alerts based on thresholds."""
        try:
            current_time = time.time()
            
            # Check recent metrics against thresholds
            recent_metrics = [m for m in self.metrics_cache 
                            if current_time - m.timestamp < 60.0]  # Last minute
            
            for metric in recent_metrics:
                if metric.parameter_name in self.performance_thresholds:
                    thresholds = self.performance_thresholds[metric.parameter_name]
                    
                    alert_level = None
                    threshold_value = None
                    
                    if "critical" in thresholds and metric.value >= thresholds["critical"]:
                        alert_level = AlertLevel.CRITICAL
                        threshold_value = thresholds["critical"]
                    elif "warning" in thresholds and metric.value >= thresholds["warning"]:
                        alert_level = AlertLevel.WARNING
                        threshold_value = thresholds["warning"]
                    
                    if alert_level:
                        # Check if we already have an active alert for this parameter
                        existing_alert = next(
                            (a for a in self.active_alerts 
                             if a.parameter == metric.parameter_name and not a.resolved),
                            None
                        )
                        
                        if not existing_alert:
                            alert = PerformanceAlert(
                                alert_id=f"{metric.parameter_name}_{int(current_time)}",
                                timestamp=current_time,
                                level=alert_level,
                                metric_type=metric.metric_type,
                                parameter=metric.parameter_name,
                                current_value=metric.value,
                                threshold_value=threshold_value,
                                message=f"{metric.parameter_name} {alert_level.value}: {metric.value} {metric.unit}"
                            )
                            
                            self.active_alerts.append(alert)
                            await self._save_alert_to_db(alert)
                            self.stats["alerts_generated"] += 1
                            
                            self.logger.warning(f"🚨 Performance Alert: {alert.message}")
                            
        except Exception as e:
            self.logger.error(f"Alert checking error: {e}")
    
    async def _manage_sessions(self) -> None:
        """Manage driving session lifecycle."""
        try:
            current_time = time.time()
            
            # Get current vehicle speed
            speed_param = await self.vehicle_manager.get_parameter("vehicle_speed")
            current_speed = float(speed_param.value) if speed_param else 0.0
            
            # Check if we should start a new session
            if not self.current_session and current_speed > self.session_start_speed_threshold:
                await self._start_session()
            
            # Check if we should end the current session
            elif self.current_session:
                if current_speed > 0:
                    self.last_activity_time = current_time
                else:
                    idle_time = current_time - self.last_activity_time
                    if idle_time > self.session_end_idle_time:
                        await self._end_session()
                
                # Update session metrics
                if current_speed > 0:
                    await self._update_session_metrics(current_speed, current_time)
                    
        except Exception as e:
            self.logger.error(f"Session management error: {e}")
    
    async def _start_session(self) -> None:
        """Start a new driving session."""
        try:
            session_id = f"session_{int(time.time())}"
            self.current_session = PerformanceSession(
                session_id=session_id,
                start_time=time.time(),
                end_time=None,
                total_distance=0.0,
                total_fuel_used=0.0,
                max_speed=0.0,
                avg_speed=0.0,
                max_engine_temp=0.0,
                avg_engine_temp=0.0,
                max_rpm=0.0,
                avg_rpm=0.0,
                fuel_economy=0.0,
                session_duration=0.0,
                idle_time=0.0,
                driving_time=0.0
            )
            
            self.logger.info(f"🚗 Started new session: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Session start error: {e}")
    
    async def _end_session(self) -> None:
        """End the current driving session."""
        try:
            if not self.current_session:
                return
            
            self.current_session.end_time = time.time()
            self.current_session.session_duration = (
                self.current_session.end_time - self.current_session.start_time
            )
            
            # Calculate final metrics
            await self._finalize_session_metrics()
            
            # Save session to database
            await self._save_session_to_db(self.current_session)
            
            self.stats["total_sessions"] += 1
            self.logger.info(f"🏁 Ended session: {self.current_session.session_id}")
            
            self.current_session = None
            
        except Exception as e:
            self.logger.error(f"Session end error: {e}")
    
    async def _update_session_metrics(self, current_speed: float, current_time: float) -> None:
        """Update current session metrics."""
        try:
            if not self.current_session:
                return
            
            # Update speed metrics
            if current_speed > self.current_session.max_speed:
                self.current_session.max_speed = current_speed
            
            # Update distance (simplified calculation)
            time_delta = self.collection_interval / 3600.0  # Convert to hours
            distance_delta = current_speed * time_delta
            self.current_session.total_distance += distance_delta
            
            # Get engine parameters for session tracking
            engine_temp_param = await self.vehicle_manager.get_parameter("engine_temp")
            if engine_temp_param:
                temp = float(engine_temp_param.value)
                if temp > self.current_session.max_engine_temp:
                    self.current_session.max_engine_temp = temp
            
            rpm_param = await self.vehicle_manager.get_parameter("engine_rpm")
            if rpm_param:
                rpm = float(rpm_param.value)
                if rpm > self.current_session.max_rpm:
                    self.current_session.max_rpm = rpm
                    
        except Exception as e:
            self.logger.error(f"Session update error: {e}")
    
    async def _finalize_session_metrics(self) -> None:
        """Calculate final session metrics."""
        try:
            if not self.current_session:
                return
            
            # Get session metrics from database
            session_metrics = await self._get_session_metrics(self.current_session.session_id)
            
            if session_metrics:
                speeds = [m.value for m in session_metrics if m.parameter_name == "vehicle_speed"]
                if speeds:
                    self.current_session.avg_speed = statistics.mean(speeds)
                
                temps = [m.value for m in session_metrics if m.parameter_name == "engine_temp"]
                if temps:
                    self.current_session.avg_engine_temp = statistics.mean(temps)
                
                rpms = [m.value for m in session_metrics if m.parameter_name == "engine_rpm"]
                if rpms:
                    self.current_session.avg_rpm = statistics.mean(rpms)
                
                # Calculate fuel economy
                if self.current_session.total_distance > 0 and self.current_session.total_fuel_used > 0:
                    self.current_session.fuel_economy = (
                        self.current_session.total_distance / self.current_session.total_fuel_used
                    )
                    
        except Exception as e:
            self.logger.error(f"Session finalization error: {e}")
    
    async def _flush_metrics_to_db(self) -> None:
        """Flush cached metrics to database."""
        try:
            if not self.metrics_cache:
                return
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metrics_data = []
                for metric in self.metrics_cache:
                    metrics_data.append((
                        metric.timestamp,
                        metric.metric_type.value,
                        metric.parameter_name,
                        metric.value,
                        metric.unit,
                        metric.source,
                        metric.vehicle_speed,
                        metric.engine_load,
                        metric.ambient_temp,
                        metric.session_id
                    ))
                
                cursor.executemany("""
                    INSERT INTO performance_metrics 
                    (timestamp, metric_type, parameter_name, value, unit, source,
                     vehicle_speed, engine_load, ambient_temp, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, metrics_data)
                
                conn.commit()
                
                self.logger.debug(f"Flushed {len(self.metrics_cache)} metrics to database")
                self.metrics_cache.clear()
                
        except Exception as e:
            self.logger.error(f"Database flush error: {e}")
    
    async def _save_session_to_db(self, session: PerformanceSession) -> None:
        """Save session data to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_id, start_time, end_time, total_distance, total_fuel_used,
                     max_speed, avg_speed, max_engine_temp, avg_engine_temp,
                     max_rpm, avg_rpm, fuel_economy, session_duration, idle_time, driving_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id, session.start_time, session.end_time,
                    session.total_distance, session.total_fuel_used,
                    session.max_speed, session.avg_speed,
                    session.max_engine_temp, session.avg_engine_temp,
                    session.max_rpm, session.avg_rpm,
                    session.fuel_economy, session.session_duration,
                    session.idle_time, session.driving_time
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Session save error: {e}")
    
    async def _save_alert_to_db(self, alert: PerformanceAlert) -> None:
        """Save alert to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO alerts 
                    (alert_id, timestamp, level, metric_type, parameter,
                     current_value, threshold_value, message, acknowledged, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id, alert.timestamp, alert.level.value,
                    alert.metric_type.value, alert.parameter,
                    alert.current_value, alert.threshold_value,
                    alert.message, alert.acknowledged, alert.resolved
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Alert save error: {e}")
    
    async def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for the specified number of days."""
        try:
            end_time = time.time()
            start_time = end_time - (days * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Session summary
                cursor.execute("""
                    SELECT COUNT(*), SUM(total_distance), SUM(total_fuel_used),
                           AVG(fuel_economy), AVG(max_engine_temp), AVG(avg_speed)
                    FROM sessions
                    WHERE start_time >= ?
                """, (start_time,))
                
                session_data = cursor.fetchone()
                
                # Alert summary
                cursor.execute("""
                    SELECT level, COUNT(*)
                    FROM alerts
                    WHERE timestamp >= ?
                    GROUP BY level
                """, (start_time,))
                
                alert_data = cursor.fetchall()
                
                return {
                    "period_days": days,
                    "total_sessions": session_data[0] or 0,
                    "total_distance": session_data[1] or 0.0,
                    "total_fuel_used": session_data[2] or 0.0,
                    "avg_fuel_economy": session_data[3] or 0.0,
                    "avg_max_engine_temp": session_data[4] or 0.0,
                    "avg_speed": session_data[5] or 0.0,
                    "alerts_by_level": {level: count for level, count in alert_data},
                    "stats": self.stats.copy()
                }
                
        except Exception as e:
            self.logger.error(f"Performance summary error: {e}")
            return {"error": str(e)}
    
    async def get_performance_trends(self, parameter: str, days: int = 30) -> PerformanceTrend:
        """Analyze performance trends for a specific parameter."""
        try:
            end_time = time.time()
            start_time = end_time - (days * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT value, timestamp
                    FROM performance_metrics
                    WHERE parameter_name = ? AND timestamp >= ?
                    ORDER BY timestamp
                """, (parameter, start_time))
                
                data = cursor.fetchall()
                
                if not data:
                    return PerformanceTrend(
                        parameter=parameter,
                        time_period=f"{days}d",
                        trend_direction="insufficient_data",
                        trend_strength=0.0,
                        avg_value=0.0,
                        min_value=0.0,
                        max_value=0.0,
                        std_deviation=0.0,
                        data_points=0
                    )
                
                values = [row[0] for row in data]
                
                # Calculate basic statistics
                avg_value = statistics.mean(values)
                min_value = min(values)
                max_value = max(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
                
                # Simple trend analysis (linear regression would be better)
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                if first_half and second_half:
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    change_pct = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
                    
                    if abs(change_pct) < 5:
                        trend_direction = "stable"
                        trend_strength = 0.0
                    elif change_pct > 0:
                        trend_direction = "increasing"
                        trend_strength = min(abs(change_pct) / 20.0, 1.0)  # Normalize to 0-1
                    else:
                        trend_direction = "decreasing"
                        trend_strength = min(abs(change_pct) / 20.0, 1.0)
                else:
                    trend_direction = "insufficient_data"
                    trend_strength = 0.0
                
                return PerformanceTrend(
                    parameter=parameter,
                    time_period=f"{days}d",
                    trend_direction=trend_direction,
                    trend_strength=trend_strength,
                    avg_value=avg_value,
                    min_value=min_value,
                    max_value=max_value,
                    std_deviation=std_dev,
                    data_points=len(values)
                )
                
        except Exception as e:
            self.logger.error(f"Trend analysis error: {e}")
            return PerformanceTrend(
                parameter=parameter,
                time_period=f"{days}d",
                trend_direction="error",
                trend_strength=0.0,
                avg_value=0.0,
                min_value=0.0,
                max_value=0.0,
                std_deviation=0.0,
                data_points=0
            )
    
    async def _get_session_metrics(self, session_id: str) -> List[PerformanceMetric]:
        """Get all metrics for a specific session."""
        try:
            # Check cache first
            cached_metrics = [m for m in self.metrics_cache if m.session_id == session_id]
            
            # Then check database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT timestamp, metric_type, parameter_name, value, unit, source,
                           vehicle_speed, engine_load, ambient_temp, session_id
                    FROM performance_metrics
                    WHERE session_id = ?
                """, (session_id,))
                
                db_metrics = []
                for row in cursor.fetchall():
                    metric = PerformanceMetric(
                        timestamp=row[0],
                        metric_type=MetricType(row[1]),
                        parameter_name=row[2],
                        value=row[3],
                        unit=row[4],
                        source=row[5],
                        vehicle_speed=row[6],
                        engine_load=row[7],
                        ambient_temp=row[8],
                        session_id=row[9]
                    )
                    db_metrics.append(metric)
                
                return cached_metrics + db_metrics
                
        except Exception as e:
            self.logger.error(f"Session metrics retrieval error: {e}")
            return []
    
    async def export_performance_data(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None,
                                    format: str = "json") -> str:
        """Export performance data to file."""
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()
            
            start_timestamp = start_date.timestamp()
            end_timestamp = end_date.timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Export metrics
                cursor.execute("""
                    SELECT * FROM performance_metrics
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                """, (start_timestamp, end_timestamp))
                
                metrics_data = cursor.fetchall()
                
                # Export sessions
                cursor.execute("""
                    SELECT * FROM sessions
                    WHERE start_time BETWEEN ? AND ?
                    ORDER BY start_time
                """, (start_timestamp, end_timestamp))
                
                sessions_data = cursor.fetchall()
                
                # Export alerts
                cursor.execute("""
                    SELECT * FROM alerts
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                """, (start_timestamp, end_timestamp))
                
                alerts_data = cursor.fetchall()
            
            # Create export data structure
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics_count": len(metrics_data),
                "sessions_count": len(sessions_data),
                "alerts_count": len(alerts_data),
                "metrics": metrics_data,
                "sessions": sessions_data,
                "alerts": alerts_data
            }
            
            # Save to file
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_export_{timestamp_str}.{format}"
            export_path = self.data_directory / filename
            
            if format == "json":
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"📄 Performance data exported to {export_path}")
            return str(export_path)
            
        except Exception as e:
            self.logger.error(f"Data export error: {e}")
            return ""
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get current active alerts."""
        return [alert for alert in self.active_alerts if not alert.resolved]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert."""
        try:
            alert = next((a for a in self.active_alerts if a.alert_id == alert_id), None)
            if alert:
                alert.acknowledged = True
                
                # Update in database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE alerts SET acknowledged = TRUE WHERE alert_id = ?
                    """, (alert_id,))
                    conn.commit()
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Alert acknowledgment error: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert."""
        try:
            alert = next((a for a in self.active_alerts if a.alert_id == alert_id), None)
            if alert:
                alert.resolved = True
                
                # Update in database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE alerts SET resolved = TRUE WHERE alert_id = ?
                    """, (alert_id,))
                    conn.commit()
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Alert resolution error: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown performance monitoring system."""
        self.logger.info("🛑 Shutting down Performance Monitor...")
        
        await self.stop_monitoring()
        
        # Flush any remaining cached data
        if self.metrics_cache:
            await self._flush_metrics_to_db()
        
        self.logger.info("✅ Performance Monitor shutdown complete")