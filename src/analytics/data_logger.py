"""
Data Logger - Specialized data collection and export for vehicle analytics
"""

import asyncio
import logging
import time
import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
import sqlite3
import threading
from queue import Queue, Empty
import gzip
import pickle


class LogLevel(Enum):
    """Data logging levels."""
    MINIMAL = "minimal"      # Basic engine parameters only
    STANDARD = "standard"    # Common performance metrics
    DETAILED = "detailed"    # All available parameters
    DIAGNOSTIC = "diagnostic" # Maximum detail for troubleshooting


class DataFormat(Enum):
    """Supported data export formats."""
    CSV = "csv"
    JSON = "json"
    BINARY = "binary"
    SQLITE = "sqlite"


@dataclass
class LoggingConfig:
    """Configuration for data logging."""
    log_level: LogLevel = LogLevel.STANDARD
    collection_interval: float = 1.0  # seconds
    buffer_size: int = 1000
    auto_export_interval: int = 3600  # seconds (1 hour)
    compression_enabled: bool = True
    retention_days: int = 30
    export_formats: List[DataFormat] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = [DataFormat.CSV, DataFormat.JSON]


@dataclass
class DataPoint:
    """Individual data point for logging."""
    timestamp: float
    parameter: str
    value: Union[float, int, str, bool]
    unit: str
    source: str
    quality: float  # 0.0 to 1.0, data quality/confidence
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LogSession:
    """Data logging session information."""
    session_id: str
    start_time: float
    end_time: Optional[float]
    log_level: LogLevel
    total_points: int
    file_paths: List[str]
    compression_ratio: Optional[float] = None


class CircularBuffer:
    """Memory-efficient circular buffer for data points."""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.buffer = [None] * max_size
        self.head = 0
        self.size = 0
        self.lock = threading.Lock()
    
    def append(self, item: DataPoint) -> None:
        """Add item to buffer."""
        with self.lock:
            self.buffer[self.head] = item
            self.head = (self.head + 1) % self.max_size
            if self.size < self.max_size:
                self.size += 1
    
    def get_all(self) -> List[DataPoint]:
        """Get all items from buffer."""
        with self.lock:
            if self.size < self.max_size:
                return [item for item in self.buffer[:self.size] if item is not None]
            else:
                # Buffer is full, return in correct order
                return ([item for item in self.buffer[self.head:] if item is not None] +
                       [item for item in self.buffer[:self.head] if item is not None])
    
    def clear(self) -> None:
        """Clear the buffer."""
        with self.lock:
            self.buffer = [None] * self.max_size
            self.head = 0
            self.size = 0
    
    def is_full(self) -> bool:
        """Check if buffer is full."""
        with self.lock:
            return self.size >= self.max_size


class DataLogger:
    """Comprehensive data logging system for vehicle analytics."""
    
    def __init__(self, 
                 config: LoggingConfig,
                 data_directory: str = "data/logs",
                 vehicle_manager=None):
        
        self.config = config
        self.data_directory = Path(data_directory)
        self.vehicle_manager = vehicle_manager
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        # Logging state
        self.logging_active = False
        self.current_session: Optional[LogSession] = None
        self.logging_task: Optional[asyncio.Task] = None
        self.export_task: Optional[asyncio.Task] = None
        
        # Data buffering
        self.data_buffer = CircularBuffer(config.buffer_size)
        self.export_queue = Queue()
        
        # Parameter sets for different log levels
        self.parameter_sets = {
            LogLevel.MINIMAL: [
                "engine_rpm", "engine_temp", "vehicle_speed"
            ],
            LogLevel.STANDARD: [
                "engine_rpm", "engine_temp", "vehicle_speed", "throttle_pos",
                "oil_pressure", "fuel_level", "coolant_temp"
            ],
            LogLevel.DETAILED: [
                "engine_rpm", "engine_temp", "vehicle_speed", "throttle_pos",
                "oil_pressure", "fuel_level", "coolant_temp", "intake_temp",
                "maf_rate", "fuel_pressure", "boost_pressure", "battery_voltage",
                "alternator_output", "transmission_temp"
            ],
            LogLevel.DIAGNOSTIC: [
                # All available parameters - populated dynamically
            ]
        }
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "total_data_points": 0,
            "total_exports": 0,
            "compression_savings": 0.0,
            "storage_used": 0.0,
            "last_export_time": 0.0
        }
        
        # Export callbacks
        self.export_callbacks: List[Callable[[str, DataFormat], None]] = []
    
    async def start_logging(self, session_name: Optional[str] = None) -> str:
        """Start data logging session."""
        try:
            if self.logging_active:
                self.logger.warning("Logging already active")
                return self.current_session.session_id if self.current_session else ""
            
            # Create new session
            timestamp = int(time.time())
            session_id = session_name or f"log_session_{timestamp}"
            
            self.current_session = LogSession(
                session_id=session_id,
                start_time=time.time(),
                end_time=None,
                log_level=self.config.log_level,
                total_points=0,
                file_paths=[]
            )
            
            # Start logging tasks
            self.logging_active = True
            self.logging_task = asyncio.create_task(self._logging_loop())
            self.export_task = asyncio.create_task(self._export_loop())
            
            self.logger.info(f"📊 Data logging started: {session_id}")
            self.stats["total_sessions"] += 1
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start logging: {e}")
            return ""
    
    async def stop_logging(self) -> Optional[LogSession]:
        """Stop current logging session."""
        try:
            if not self.logging_active:
                return None
            
            self.logging_active = False
            
            # Cancel tasks
            if self.logging_task:
                self.logging_task.cancel()
                try:
                    await self.logging_task
                except asyncio.CancelledError:
                    pass
            
            if self.export_task:
                self.export_task.cancel()
                try:
                    await self.export_task
                except asyncio.CancelledError:
                    pass
            
            # Finalize current session
            if self.current_session:
                self.current_session.end_time = time.time()
                
                # Export any remaining buffered data
                await self._export_buffer_data()
                
                session = self.current_session
                self.current_session = None
                
                self.logger.info(f"📊 Data logging stopped: {session.session_id}")
                return session
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to stop logging: {e}")
            return None
    
    async def _logging_loop(self) -> None:
        """Main data collection loop."""
        while self.logging_active:
            try:
                await self._collect_data_points()
                await asyncio.sleep(self.config.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Data collection error: {e}")
                await asyncio.sleep(self.config.collection_interval)
    
    async def _export_loop(self) -> None:
        """Automatic export loop."""
        while self.logging_active:
            try:
                await asyncio.sleep(self.config.auto_export_interval)
                if self.logging_active:  # Check again after sleep
                    await self._export_buffer_data()
                    
            except Exception as e:
                self.logger.error(f"Auto export error: {e}")
    
    async def _collect_data_points(self) -> None:
        """Collect data points based on current log level."""
        try:
            if not self.vehicle_manager:
                # Generate mock data for testing
                await self._collect_mock_data()
                return
            
            current_time = time.time()
            parameters = self._get_parameters_for_level(self.config.log_level)
            
            for param_name in parameters:
                try:
                    vehicle_param = await self.vehicle_manager.get_parameter(param_name)
                    if vehicle_param:
                        data_point = DataPoint(
                            timestamp=current_time,
                            parameter=param_name,
                            value=vehicle_param.value,
                            unit=vehicle_param.unit,
                            source=vehicle_param.source,
                            quality=1.0,  # Assume good quality from vehicle
                            metadata={
                                "system_type": vehicle_param.system_type.value,
                                "collection_interval": self.config.collection_interval
                            }
                        )
                        
                        self.data_buffer.append(data_point)
                        
                        if self.current_session:
                            self.current_session.total_points += 1
                        
                        self.stats["total_data_points"] += 1
                        
                except Exception as e:
                    self.logger.debug(f"Could not collect {param_name}: {e}")
            
            # Check if buffer needs flushing
            if self.data_buffer.is_full():
                await self._export_buffer_data()
                
        except Exception as e:
            self.logger.error(f"Data point collection error: {e}")
    
    async def _collect_mock_data(self) -> None:
        """Collect mock data for testing without vehicle connection."""
        import random
        
        current_time = time.time()
        parameters = self._get_parameters_for_level(self.config.log_level)
        
        # Mock data ranges
        mock_ranges = {
            "engine_rpm": (800, 6000),
            "engine_temp": (80, 110),
            "vehicle_speed": (0, 120),
            "throttle_pos": (0, 100),
            "oil_pressure": (20, 60),
            "fuel_level": (10, 100),
            "boost_pressure": (0, 15)
        }
        
        for param_name in parameters:
            if param_name in mock_ranges:
                min_val, max_val = mock_ranges[param_name]
                value = random.uniform(min_val, max_val)
                
                data_point = DataPoint(
                    timestamp=current_time,
                    parameter=param_name,
                    value=round(value, 2),
                    unit=self._get_unit_for_parameter(param_name),
                    source="mock",
                    quality=0.9,  # Mock data quality
                    metadata={"mock": True}
                )
                
                self.data_buffer.append(data_point)
                
                if self.current_session:
                    self.current_session.total_points += 1
                
                self.stats["total_data_points"] += 1
    
    def _get_parameters_for_level(self, level: LogLevel) -> List[str]:
        """Get parameter list for logging level."""
        if level == LogLevel.DIAGNOSTIC:
            # Return all available parameters
            all_params = set()
            for param_list in self.parameter_sets.values():
                all_params.update(param_list)
            return list(all_params)
        
        return self.parameter_sets.get(level, self.parameter_sets[LogLevel.STANDARD])
    
    def _get_unit_for_parameter(self, parameter: str) -> str:
        """Get appropriate unit for parameter."""
        unit_map = {
            "engine_rpm": "rpm",
            "engine_temp": "°C",
            "vehicle_speed": "km/h",
            "throttle_pos": "%",
            "oil_pressure": "PSI",
            "fuel_level": "%",
            "boost_pressure": "PSI",
            "battery_voltage": "V"
        }
        return unit_map.get(parameter, "unit")
    
    async def _export_buffer_data(self) -> None:
        """Export buffered data to files."""
        try:
            if not self.current_session:
                return
            
            data_points = self.data_buffer.get_all()
            if not data_points:
                return
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for format_type in self.config.export_formats:
                filename = f"{self.current_session.session_id}_{timestamp_str}.{format_type.value}"
                file_path = self.data_directory / filename
                
                try:
                    if format_type == DataFormat.CSV:
                        await self._export_to_csv(data_points, file_path)
                    elif format_type == DataFormat.JSON:
                        await self._export_to_json(data_points, file_path)
                    elif format_type == DataFormat.BINARY:
                        await self._export_to_binary(data_points, file_path)
                    elif format_type == DataFormat.SQLITE:
                        await self._export_to_sqlite(data_points, file_path)
                    
                    # Compress if enabled
                    if self.config.compression_enabled:
                        compressed_path = await self._compress_file(file_path)
                        if compressed_path:
                            self.current_session.file_paths.append(str(compressed_path))
                        else:
                            self.current_session.file_paths.append(str(file_path))
                    else:
                        self.current_session.file_paths.append(str(file_path))
                    
                    # Notify callbacks
                    for callback in self.export_callbacks:
                        try:
                            callback(str(file_path), format_type)
                        except Exception as e:
                            self.logger.error(f"Export callback error: {e}")
                    
                except Exception as e:
                    self.logger.error(f"Export to {format_type.value} failed: {e}")
            
            # Clear buffer after successful export
            self.data_buffer.clear()
            self.stats["total_exports"] += 1
            self.stats["last_export_time"] = time.time()
            
            self.logger.debug(f"Exported {len(data_points)} data points")
            
        except Exception as e:
            self.logger.error(f"Buffer export error: {e}")
    
    async def _export_to_csv(self, data_points: List[DataPoint], file_path: Path) -> None:
        """Export data points to CSV format."""
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'parameter', 'value', 'unit', 'source', 'quality']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for point in data_points:
                writer.writerow({
                    'timestamp': point.timestamp,
                    'parameter': point.parameter,
                    'value': point.value,
                    'unit': point.unit,
                    'source': point.source,
                    'quality': point.quality
                })
    
    async def _export_to_json(self, data_points: List[DataPoint], file_path: Path) -> None:
        """Export data points to JSON format."""
        data = {
            'session_id': self.current_session.session_id if self.current_session else None,
            'export_time': time.time(),
            'log_level': self.config.log_level.value,
            'data_points': [asdict(point) for point in data_points]
        }
        
        with open(file_path, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2, default=str)
    
    async def _export_to_binary(self, data_points: List[DataPoint], file_path: Path) -> None:
        """Export data points to binary format (pickle)."""
        data = {
            'session_id': self.current_session.session_id if self.current_session else None,
            'export_time': time.time(),
            'log_level': self.config.log_level,
            'data_points': data_points
        }
        
        with open(file_path, 'wb') as binfile:
            pickle.dump(data, binfile)
    
    async def _export_to_sqlite(self, data_points: List[DataPoint], file_path: Path) -> None:
        """Export data points to SQLite database."""
        with sqlite3.connect(file_path) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    parameter TEXT NOT NULL,
                    value TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    source TEXT NOT NULL,
                    quality REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Insert data points
            for point in data_points:
                cursor.execute("""
                    INSERT INTO data_points 
                    (timestamp, parameter, value, unit, source, quality, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    point.timestamp,
                    point.parameter,
                    str(point.value),
                    point.unit,
                    point.source,
                    point.quality,
                    json.dumps(point.metadata) if point.metadata else None
                ))
            
            conn.commit()
    
    async def _compress_file(self, file_path: Path) -> Optional[Path]:
        """Compress file using gzip."""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Calculate compression ratio
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            
            if compressed_size < original_size:
                compression_ratio = compressed_size / original_size
                self.stats["compression_savings"] += (1 - compression_ratio) * original_size
                
                if self.current_session:
                    self.current_session.compression_ratio = compression_ratio
                
                # Remove original file
                file_path.unlink()
                
                return compressed_path
            else:
                # Compression didn't help, remove compressed file
                compressed_path.unlink()
                return file_path
                
        except Exception as e:
            self.logger.error(f"File compression error: {e}")
            return file_path
    
    async def change_log_level(self, new_level: LogLevel) -> None:
        """Change logging level during active session."""
        old_level = self.config.log_level
        self.config.log_level = new_level
        
        self.logger.info(f"📊 Log level changed: {old_level.value} -> {new_level.value}")
        
        if self.current_session:
            self.current_session.log_level = new_level
    
    def add_export_callback(self, callback: Callable[[str, DataFormat], None]) -> None:
        """Add callback to be called when data is exported."""
        self.export_callbacks.append(callback)
    
    def remove_export_callback(self, callback: Callable[[str, DataFormat], None]) -> None:
        """Remove export callback."""
        if callback in self.export_callbacks:
            self.export_callbacks.remove(callback)
    
    async def export_session_data(self, 
                                session_id: str, 
                                start_time: Optional[float] = None,
                                end_time: Optional[float] = None,
                                format_type: DataFormat = DataFormat.JSON) -> Optional[str]:
        """Export specific session data."""
        try:
            # For now, export current buffer data
            # In a full implementation, would query database or files
            
            data_points = self.data_buffer.get_all()
            
            if start_time or end_time:
                filtered_points = []
                for point in data_points:
                    if start_time and point.timestamp < start_time:
                        continue
                    if end_time and point.timestamp > end_time:
                        continue
                    filtered_points.append(point)
                data_points = filtered_points
            
            if not data_points:
                return None
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{session_id}_{timestamp_str}.{format_type.value}"
            file_path = self.data_directory / filename
            
            if format_type == DataFormat.CSV:
                await self._export_to_csv(data_points, file_path)
            elif format_type == DataFormat.JSON:
                await self._export_to_json(data_points, file_path)
            elif format_type == DataFormat.BINARY:
                await self._export_to_binary(data_points, file_path)
            elif format_type == DataFormat.SQLITE:
                await self._export_to_sqlite(data_points, file_path)
            
            self.logger.info(f"📄 Session data exported: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Session export error: {e}")
            return None
    
    async def cleanup_old_files(self) -> None:
        """Clean up old log files based on retention policy."""
        try:
            cutoff_time = time.time() - (self.config.retention_days * 24 * 3600)
            
            removed_count = 0
            total_size_removed = 0
            
            for file_path in self.data_directory.iterdir():
                if file_path.is_file():
                    file_time = file_path.stat().st_mtime
                    if file_time < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        removed_count += 1
                        total_size_removed += file_size
            
            if removed_count > 0:
                self.logger.info(f"🧹 Cleaned up {removed_count} old files ({total_size_removed/1024/1024:.1f} MB)")
                
        except Exception as e:
            self.logger.error(f"File cleanup error: {e}")
    
    def get_logging_status(self) -> Dict[str, Any]:
        """Get current logging status."""
        return {
            "logging_active": self.logging_active,
            "current_session": asdict(self.current_session) if self.current_session else None,
            "log_level": self.config.log_level.value,
            "buffer_size": self.data_buffer.size,
            "buffer_full": self.data_buffer.is_full(),
            "stats": self.stats.copy(),
            "config": {
                "collection_interval": self.config.collection_interval,
                "buffer_size": self.config.buffer_size,
                "auto_export_interval": self.config.auto_export_interval,
                "compression_enabled": self.config.compression_enabled,
                "retention_days": self.config.retention_days,
                "export_formats": [f.value for f in self.config.export_formats]
            }
        }
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.data_directory.iterdir():
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            self.stats["storage_used"] = total_size
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": total_size / 1024 / 1024,
                "file_count": file_count,
                "compression_savings_mb": self.stats["compression_savings"] / 1024 / 1024,
                "data_directory": str(self.data_directory)
            }
            
        except Exception as e:
            self.logger.error(f"Storage usage calculation error: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown data logger."""
        self.logger.info("🛑 Shutting down Data Logger...")
        
        # Stop logging if active
        session = await self.stop_logging()
        
        # Clean up old files
        await self.cleanup_old_files()
        
        self.logger.info("✅ Data Logger shutdown complete")
        
        return session