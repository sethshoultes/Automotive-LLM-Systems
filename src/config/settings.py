"""
Configuration management for Automotive LLM System
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import yaml
from pydantic import BaseModel, Field


class AudioSettings(BaseModel):
    """Audio system configuration."""
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(default=1024, description="Audio chunk size for processing")
    input_device_index: Optional[int] = Field(default=None, description="Audio input device index")
    wake_word_sensitivity: float = Field(default=0.7, description="Wake word detection sensitivity")
    noise_reduction: bool = Field(default=True, description="Enable audio noise reduction")


class VehicleSettings(BaseModel):
    """Vehicle interface configuration."""
    obd_port: str = Field(default="/dev/ttyUSB0", description="OBD-II port")
    obd_baudrate: int = Field(default=38400, description="OBD-II baud rate")
    can_channel: str = Field(default="can0", description="CAN bus interface")
    can_bitrate: int = Field(default=500000, description="CAN bus bit rate")
    enable_obd: bool = Field(default=True, description="Enable OBD-II interface")
    enable_can: bool = Field(default=True, description="Enable CAN bus interface")
    vehicle_make: str = Field(default="generic", description="Vehicle manufacturer")
    vehicle_model: str = Field(default="unknown", description="Vehicle model")
    vehicle_year: int = Field(default=2000, description="Vehicle year")


class LLMSettings(BaseModel):
    """LLM configuration."""
    model_name: str = Field(default="llama3.1:8b-instruct-q4_K_M", description="LLM model name")
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama server URL")
    max_tokens: int = Field(default=512, description="Maximum response tokens")
    temperature: float = Field(default=0.7, description="LLM temperature")
    context_window: int = Field(default=4096, description="Context window size")
    enable_hailo: bool = Field(default=True, description="Enable Hailo AI acceleration")


class SafetySettings(BaseModel):
    """Safety system configuration."""
    enable_monitoring: bool = Field(default=True, description="Enable safety monitoring")
    monitoring_interval: float = Field(default=1.0, description="Monitoring interval in seconds")
    engine_temp_warning: float = Field(default=105.0, description="Engine temp warning limit °C")
    engine_temp_critical: float = Field(default=110.0, description="Engine temp critical limit °C")
    max_boost_pressure: float = Field(default=20.0, description="Maximum boost pressure PSI")
    max_rpm: float = Field(default=7000.0, description="Maximum RPM limit")
    emergency_mode_enabled: bool = Field(default=True, description="Enable emergency mode")


class HVACSettings(BaseModel):
    """HVAC system configuration."""
    min_temperature: float = Field(default=16.0, description="Minimum temperature °C")
    max_temperature: float = Field(default=32.0, description="Maximum temperature °C")
    max_fan_speed: int = Field(default=8, description="Maximum fan speed level")
    auto_mode_enabled: bool = Field(default=True, description="Enable auto mode")
    dual_zone: bool = Field(default=False, description="Dual zone climate control")


class LoggingSettings(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Log level")
    file_path: str = Field(default="/var/log/automotive-llm/system.log", description="Log file path")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes")
    backup_count: int = Field(default=5, description="Number of backup log files")
    enable_console: bool = Field(default=True, description="Enable console logging")
    enable_file: bool = Field(default=True, description="Enable file logging")


class SystemSettings(BaseModel):
    """System-level configuration."""
    device_name: str = Field(default="automotive-llm", description="Device name")
    enable_api: bool = Field(default=False, description="Enable REST API")
    api_port: int = Field(default=8000, description="API server port")
    data_directory: str = Field(default="/var/lib/automotive-llm", description="Data directory")
    config_directory: str = Field(default="/etc/automotive-llm", description="Config directory")
    enable_systemd: bool = Field(default=True, description="Enable systemd integration")


class Settings:
    """Main configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.logger = logging.getLogger(__name__)
        
        # Initialize default settings
        self.audio = AudioSettings()
        self.vehicle = VehicleSettings()
        self.llm = LLMSettings()
        self.safety = SafetySettings()
        self.hvac = HVACSettings()
        self.logging = LoggingSettings()
        self.system = SystemSettings()
        
        # Load configuration from file
        self._load_config()
        
        # Environment variable overrides
        self._apply_env_overrides()
        
        # Derived properties
        self.log_level = self.logging.level
        self.log_file = self.logging.file_path
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_paths = [
            "config.yaml",
            "config/config.yaml",
            "/etc/automotive-llm/config.yaml",
            os.path.expanduser("~/.config/automotive-llm/config.yaml"),
            "/usr/local/etc/automotive-llm/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path or not os.path.exists(self.config_path):
            self.logger.info("No configuration file found, using defaults")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return
            
            # Update settings from config file
            if 'audio' in config_data:
                self.audio = AudioSettings(**config_data['audio'])
            
            if 'vehicle' in config_data:
                self.vehicle = VehicleSettings(**config_data['vehicle'])
            
            if 'llm' in config_data:
                self.llm = LLMSettings(**config_data['llm'])
            
            if 'safety' in config_data:
                self.safety = SafetySettings(**config_data['safety'])
            
            if 'hvac' in config_data:
                self.hvac = HVACSettings(**config_data['hvac'])
            
            if 'logging' in config_data:
                self.logging = LoggingSettings(**config_data['logging'])
            
            if 'system' in config_data:
                self.system = SystemSettings(**config_data['system'])
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            # Audio settings
            "AUTOMOTIVE_LLM_AUDIO_SAMPLE_RATE": ("audio", "sample_rate", int),
            "AUTOMOTIVE_LLM_WAKE_WORD_SENSITIVITY": ("audio", "wake_word_sensitivity", float),
            
            # Vehicle settings
            "AUTOMOTIVE_LLM_OBD_PORT": ("vehicle", "obd_port", str),
            "AUTOMOTIVE_LLM_CAN_CHANNEL": ("vehicle", "can_channel", str),
            "AUTOMOTIVE_LLM_VEHICLE_MAKE": ("vehicle", "vehicle_make", str),
            
            # LLM settings
            "AUTOMOTIVE_LLM_MODEL_NAME": ("llm", "model_name", str),
            "AUTOMOTIVE_LLM_OLLAMA_HOST": ("llm", "ollama_host", str),
            "AUTOMOTIVE_LLM_ENABLE_HAILO": ("llm", "enable_hailo", bool),
            
            # Safety settings
            "AUTOMOTIVE_LLM_ENGINE_TEMP_WARNING": ("safety", "engine_temp_warning", float),
            "AUTOMOTIVE_LLM_MAX_BOOST_PRESSURE": ("safety", "max_boost_pressure", float),
            
            # Logging settings
            "AUTOMOTIVE_LLM_LOG_LEVEL": ("logging", "level", str),
            "AUTOMOTIVE_LLM_LOG_FILE": ("logging", "file_path", str),
            
            # System settings
            "AUTOMOTIVE_LLM_DEVICE_NAME": ("system", "device_name", str),
            "AUTOMOTIVE_LLM_API_PORT": ("system", "api_port", int),
        }
        
        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convert string to appropriate type
                    if type_func == bool:
                        converted_value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        converted_value = type_func(value)
                    
                    # Set the value
                    section_obj = getattr(self, section)
                    setattr(section_obj, key, converted_value)
                    
                    self.logger.debug(f"Environment override: {env_var} = {converted_value}")
                    
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid environment variable {env_var}: {e}")
    
    def save_config(self, path: Optional[str] = None) -> bool:
        """Save current configuration to file."""
        save_path = path or self.config_path or "config.yaml"
        
        try:
            config_data = {
                'audio': self.audio.model_dump(),
                'vehicle': self.vehicle.model_dump(),
                'llm': self.llm.model_dump(),
                'safety': self.safety.model_dump(),
                'hvac': self.hvac.model_dump(),
                'logging': self.logging.model_dump(),
                'system': self.system.model_dump()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Validate configuration settings and return any errors."""
        errors = []
        
        # Validate audio settings
        if not (8000 <= self.audio.sample_rate <= 48000):
            errors.append(f"Invalid audio sample rate: {self.audio.sample_rate}")
        
        if not (0.0 <= self.audio.wake_word_sensitivity <= 1.0):
            errors.append(f"Invalid wake word sensitivity: {self.audio.wake_word_sensitivity}")
        
        # Validate vehicle settings
        if self.vehicle.enable_obd and not os.path.exists(self.vehicle.obd_port):
            errors.append(f"OBD port does not exist: {self.vehicle.obd_port}")
        
        # Validate safety settings
        if self.safety.engine_temp_warning >= self.safety.engine_temp_critical:
            errors.append("Engine temp warning must be less than critical limit")
        
        if self.safety.max_boost_pressure <= 0:
            errors.append("Max boost pressure must be positive")
        
        # Validate HVAC settings
        if self.hvac.min_temperature >= self.hvac.max_temperature:
            errors.append("HVAC min temperature must be less than max temperature")
        
        # Validate logging settings
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.logging.level}")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "config_file": self.config_path,
            "audio": {
                "sample_rate": self.audio.sample_rate,
                "wake_word_sensitivity": self.audio.wake_word_sensitivity,
                "noise_reduction": self.audio.noise_reduction
            },
            "vehicle": {
                "make": self.vehicle.vehicle_make,
                "model": self.vehicle.vehicle_model,
                "year": self.vehicle.vehicle_year,
                "obd_enabled": self.vehicle.enable_obd,
                "can_enabled": self.vehicle.enable_can
            },
            "llm": {
                "model": self.llm.model_name,
                "hailo_enabled": self.llm.enable_hailo
            },
            "safety": {
                "monitoring_enabled": self.safety.enable_monitoring,
                "emergency_mode": self.safety.emergency_mode_enabled
            },
            "system": {
                "device_name": self.system.device_name,
                "api_enabled": self.system.enable_api
            }
        }