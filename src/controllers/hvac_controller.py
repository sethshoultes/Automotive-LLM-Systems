"""
HVAC Controller - Climate control system management
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, List

from interfaces.vehicle import VehicleManager, VehicleParameter


class HVACMode(Enum):
    """HVAC operating modes."""
    OFF = "off"
    AUTO = "auto"
    HEAT = "heat"
    COOL = "cool"
    DEFROST = "defrost"
    VENT = "vent"


class FanSpeed(Enum):
    """Fan speed levels."""
    OFF = 0
    LOW = 2
    MEDIUM = 4
    HIGH = 6
    MAX = 8


class AirDistribution(Enum):
    """Air distribution modes."""
    FACE = "face"
    FEET = "feet"
    FACE_FEET = "face_feet"
    DEFROST = "defrost"
    DEFROST_FEET = "defrost_feet"


@dataclass
class HVACState:
    """Current HVAC system state."""
    mode: HVACMode
    driver_temp: float  # Celsius
    passenger_temp: float  # Celsius
    fan_speed: int  # 0-8
    air_distribution: AirDistribution
    recirculation: bool
    ac_enabled: bool
    auto_mode: bool
    defrost_enabled: bool
    timestamp: float


@dataclass
class HVACLimits:
    """HVAC system safety and operational limits."""
    min_temp: float = 16.0  # °C
    max_temp: float = 32.0  # °C
    min_fan_speed: int = 0
    max_fan_speed: int = 8
    defrost_temp_threshold: float = 5.0  # Auto defrost below this temp
    max_temp_difference: float = 10.0  # Max difference between zones


class HVACController:
    """Controls vehicle HVAC (heating, ventilation, air conditioning) system."""
    
    def __init__(self, vehicle_manager: VehicleManager):
        self.vehicle_manager = vehicle_manager
        self.logger = logging.getLogger(__name__)
        
        # Current state
        self.current_state = HVACState(
            mode=HVACMode.OFF,
            driver_temp=22.0,  # Default 22°C (72°F)
            passenger_temp=22.0,
            fan_speed=0,
            air_distribution=AirDistribution.FACE,
            recirculation=False,
            ac_enabled=False,
            auto_mode=False,
            defrost_enabled=False,
            timestamp=time.time()
        )
        
        # System limits
        self.limits = HVACLimits()
        
        # Performance tracking
        self.stats = {
            "commands_executed": 0,
            "temperature_changes": 0,
            "mode_changes": 0,
            "auto_adjustments": 0
        }
        
        # Auto mode parameters
        self.auto_mode_enabled = False
        self.target_temp = 22.0
        self.temp_tolerance = 1.0  # ±1°C tolerance
        
        # Mock cabin temperature for development
        self.mock_cabin_temp = 20.0
    
    async def initialize(self) -> bool:
        """Initialize HVAC controller."""
        try:
            self.logger.info("🌡️ Initializing HVAC Controller...")
            
            # Read current HVAC state from vehicle
            await self._read_current_state()
            
            self.logger.info("✅ HVAC Controller initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"HVAC Controller initialization failed: {e}")
            return False
    
    async def _read_current_state(self) -> None:
        """Read current HVAC state from vehicle systems."""
        try:
            # Try to read current temperature settings
            driver_temp_param = await self.vehicle_manager.get_parameter("hvac_driver_temp")
            if driver_temp_param:
                self.current_state.driver_temp = float(driver_temp_param.value)
            
            passenger_temp_param = await self.vehicle_manager.get_parameter("hvac_passenger_temp")
            if passenger_temp_param:
                self.current_state.passenger_temp = float(passenger_temp_param.value)
            
            fan_speed_param = await self.vehicle_manager.get_parameter("hvac_fan_speed")
            if fan_speed_param:
                self.current_state.fan_speed = int(fan_speed_param.value)
            
            self.current_state.timestamp = time.time()
            
        except Exception as e:
            self.logger.warning(f"Could not read HVAC state from vehicle: {e}")
    
    async def set_temperature(self, 
                            temperature: float, 
                            zone: str = "both", 
                            unit: str = "celsius") -> Dict[str, Any]:
        """Set target temperature for specified zone."""
        try:
            # Convert to Celsius if needed
            temp_celsius = self._convert_to_celsius(temperature, unit)
            
            # Validate temperature range
            if not self._validate_temperature(temp_celsius):
                return {
                    "success": False,
                    "error": f"Temperature {temperature}°{unit.upper()} is outside safe range ({self.limits.min_temp}-{self.limits.max_temp}°C)"
                }
            
            # Apply temperature setting
            if zone.lower() in ["driver", "both"]:
                await self._set_driver_temperature(temp_celsius)
            
            if zone.lower() in ["passenger", "both"]:
                await self._set_passenger_temperature(temp_celsius)
            
            # Update statistics
            self.stats["temperature_changes"] += 1
            self.stats["commands_executed"] += 1
            
            # Auto-enable appropriate mode
            if not self.current_state.mode or self.current_state.mode == HVACMode.OFF:
                await self._auto_select_mode(temp_celsius)
            
            temp_fahrenheit = self._celsius_to_fahrenheit(temp_celsius)
            
            self.logger.info(f"🌡️ Temperature set to {temp_celsius:.1f}°C ({temp_fahrenheit:.1f}°F) for {zone}")
            
            return {
                "success": True,
                "temperature_celsius": temp_celsius,
                "temperature_fahrenheit": temp_fahrenheit,
                "zone": zone,
                "mode": self.current_state.mode.value
            }
            
        except Exception as e:
            self.logger.error(f"Error setting temperature: {e}")
            return {"success": False, "error": str(e)}
    
    async def _set_driver_temperature(self, temp_celsius: float) -> None:
        """Set driver zone temperature."""
        self.current_state.driver_temp = temp_celsius
        await self.vehicle_manager.set_parameter("hvac_driver_temp", temp_celsius)
    
    async def _set_passenger_temperature(self, temp_celsius: float) -> None:
        """Set passenger zone temperature."""
        self.current_state.passenger_temp = temp_celsius
        await self.vehicle_manager.set_parameter("hvac_passenger_temp", temp_celsius)
    
    async def set_fan_speed(self, speed: int) -> Dict[str, Any]:
        """Set fan speed (0-8)."""
        try:
            # Validate fan speed
            if not (self.limits.min_fan_speed <= speed <= self.limits.max_fan_speed):
                return {
                    "success": False,
                    "error": f"Fan speed {speed} is outside valid range ({self.limits.min_fan_speed}-{self.limits.max_fan_speed})"
                }
            
            # Set fan speed
            self.current_state.fan_speed = speed
            await self.vehicle_manager.set_parameter("hvac_fan_speed", speed)
            
            # Update mode if turning fan off
            if speed == 0:
                self.current_state.mode = HVACMode.OFF
            elif self.current_state.mode == HVACMode.OFF:
                self.current_state.mode = HVACMode.AUTO
            
            self.stats["commands_executed"] += 1
            
            self.logger.info(f"💨 Fan speed set to {speed}")
            
            return {
                "success": True,
                "fan_speed": speed,
                "mode": self.current_state.mode.value
            }
            
        except Exception as e:
            self.logger.error(f"Error setting fan speed: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set HVAC operating mode."""
        try:
            # Parse mode
            try:
                hvac_mode = HVACMode(mode.lower())
            except ValueError:
                return {
                    "success": False,
                    "error": f"Unknown HVAC mode: {mode}. Valid modes: {[m.value for m in HVACMode]}"
                }
            
            # Apply mode changes
            await self._apply_mode(hvac_mode)
            
            self.stats["mode_changes"] += 1
            self.stats["commands_executed"] += 1
            
            self.logger.info(f"🔄 HVAC mode set to {hvac_mode.value}")
            
            return {
                "success": True,
                "mode": hvac_mode.value,
                "fan_speed": self.current_state.fan_speed,
                "ac_enabled": self.current_state.ac_enabled
            }
            
        except Exception as e:
            self.logger.error(f"Error setting HVAC mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_mode(self, mode: HVACMode) -> None:
        """Apply HVAC mode settings."""
        self.current_state.mode = mode
        
        if mode == HVACMode.OFF:
            self.current_state.fan_speed = 0
            self.current_state.ac_enabled = False
            await self.vehicle_manager.set_parameter("hvac_fan_speed", 0)
            
        elif mode == HVACMode.AUTO:
            self.auto_mode_enabled = True
            if self.current_state.fan_speed == 0:
                self.current_state.fan_speed = 3  # Default auto speed
            await self.vehicle_manager.set_parameter("hvac_fan_speed", self.current_state.fan_speed)
            
        elif mode == HVACMode.HEAT:
            self.current_state.ac_enabled = False
            if self.current_state.fan_speed == 0:
                self.current_state.fan_speed = 2
            await self.vehicle_manager.set_parameter("hvac_fan_speed", self.current_state.fan_speed)
            
        elif mode == HVACMode.COOL:
            self.current_state.ac_enabled = True
            if self.current_state.fan_speed == 0:
                self.current_state.fan_speed = 3
            await self.vehicle_manager.set_parameter("hvac_fan_speed", self.current_state.fan_speed)
            
        elif mode == HVACMode.DEFROST:
            self.current_state.defrost_enabled = True
            self.current_state.air_distribution = AirDistribution.DEFROST
            if self.current_state.fan_speed < 4:
                self.current_state.fan_speed = 4  # Higher speed for defrost
            await self.vehicle_manager.set_parameter("hvac_fan_speed", self.current_state.fan_speed)
        
        # Update vehicle systems
        await self.vehicle_manager.set_parameter("hvac_mode", mode.value)
    
    async def activate_defrost(self) -> Dict[str, Any]:
        """Activate windshield defrost."""
        try:
            self.current_state.defrost_enabled = True
            self.current_state.air_distribution = AirDistribution.DEFROST
            self.current_state.mode = HVACMode.DEFROST
            
            # Set appropriate fan speed and temperature for defrost
            if self.current_state.fan_speed < 4:
                self.current_state.fan_speed = 4
            
            # Use warm air for defrost
            if self.current_state.driver_temp < 25:
                await self._set_driver_temperature(25.0)
            
            await self.vehicle_manager.set_parameter("hvac_defrost", True)
            await self.vehicle_manager.set_parameter("hvac_fan_speed", self.current_state.fan_speed)
            
            self.stats["commands_executed"] += 1
            
            self.logger.info("🌬️ Defrost activated")
            
            return {
                "success": True,
                "mode": "defrost",
                "fan_speed": self.current_state.fan_speed,
                "message": "Windshield defrost activated"
            }
            
        except Exception as e:
            self.logger.error(f"Error activating defrost: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_air_distribution(self, distribution: str) -> Dict[str, Any]:
        """Set air distribution mode."""
        try:
            try:
                air_dist = AirDistribution(distribution.lower())
            except ValueError:
                return {
                    "success": False,
                    "error": f"Unknown air distribution: {distribution}. Valid options: {[d.value for d in AirDistribution]}"
                }
            
            self.current_state.air_distribution = air_dist
            await self.vehicle_manager.set_parameter("hvac_air_distribution", air_dist.value)
            
            self.stats["commands_executed"] += 1
            
            self.logger.info(f"🌀 Air distribution set to {air_dist.value}")
            
            return {
                "success": True,
                "air_distribution": air_dist.value
            }
            
        except Exception as e:
            self.logger.error(f"Error setting air distribution: {e}")
            return {"success": False, "error": str(e)}
    
    async def toggle_ac(self) -> Dict[str, Any]:
        """Toggle air conditioning on/off."""
        try:
            self.current_state.ac_enabled = not self.current_state.ac_enabled
            await self.vehicle_manager.set_parameter("hvac_ac_enabled", self.current_state.ac_enabled)
            
            # Adjust mode based on AC state
            if self.current_state.ac_enabled:
                if self.current_state.mode == HVACMode.HEAT:
                    self.current_state.mode = HVACMode.COOL
            
            self.stats["commands_executed"] += 1
            
            status = "on" if self.current_state.ac_enabled else "off"
            self.logger.info(f"❄️ Air conditioning turned {status}")
            
            return {
                "success": True,
                "ac_enabled": self.current_state.ac_enabled,
                "mode": self.current_state.mode.value,
                "message": f"Air conditioning {status}"
            }
            
        except Exception as e:
            self.logger.error(f"Error toggling AC: {e}")
            return {"success": False, "error": str(e)}
    
    async def enable_auto_mode(self, target_temp: float, unit: str = "celsius") -> Dict[str, Any]:
        """Enable automatic climate control."""
        try:
            temp_celsius = self._convert_to_celsius(target_temp, unit)
            
            if not self._validate_temperature(temp_celsius):
                return {
                    "success": False,
                    "error": f"Target temperature outside safe range"
                }
            
            self.auto_mode_enabled = True
            self.target_temp = temp_celsius
            self.current_state.auto_mode = True
            self.current_state.mode = HVACMode.AUTO
            
            # Set initial temperature
            await self._set_driver_temperature(temp_celsius)
            await self._set_passenger_temperature(temp_celsius)
            
            self.stats["commands_executed"] += 1
            
            temp_fahrenheit = self._celsius_to_fahrenheit(temp_celsius)
            self.logger.info(f"🤖 Auto mode enabled, target: {temp_celsius:.1f}°C ({temp_fahrenheit:.1f}°F)")
            
            return {
                "success": True,
                "auto_mode": True,
                "target_temperature_celsius": temp_celsius,
                "target_temperature_fahrenheit": temp_fahrenheit
            }
            
        except Exception as e:
            self.logger.error(f"Error enabling auto mode: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current HVAC system status."""
        try:
            # Get current cabin temperature (mock for now)
            cabin_temp = await self._get_cabin_temperature()
            
            return {
                "mode": self.current_state.mode.value,
                "driver_temp_celsius": self.current_state.driver_temp,
                "driver_temp_fahrenheit": self._celsius_to_fahrenheit(self.current_state.driver_temp),
                "passenger_temp_celsius": self.current_state.passenger_temp,
                "passenger_temp_fahrenheit": self._celsius_to_fahrenheit(self.current_state.passenger_temp),
                "fan_speed": self.current_state.fan_speed,
                "air_distribution": self.current_state.air_distribution.value,
                "ac_enabled": self.current_state.ac_enabled,
                "auto_mode": self.current_state.auto_mode,
                "defrost_enabled": self.current_state.defrost_enabled,
                "recirculation": self.current_state.recirculation,
                "cabin_temperature_celsius": cabin_temp,
                "cabin_temperature_fahrenheit": self._celsius_to_fahrenheit(cabin_temp),
                "timestamp": self.current_state.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error getting HVAC status: {e}")
            return {"error": str(e)}
    
    async def _get_cabin_temperature(self) -> float:
        """Get current cabin temperature."""
        # In real implementation, would read from cabin temperature sensor
        # For now, simulate cabin temperature based on HVAC operation
        
        if self.current_state.mode == HVACMode.OFF:
            # Cabin temperature slowly approaches outside temperature
            self.mock_cabin_temp += (20.0 - self.mock_cabin_temp) * 0.1
        else:
            # Cabin temperature moves toward target temperature
            target = (self.current_state.driver_temp + self.current_state.passenger_temp) / 2
            adjustment_rate = self.current_state.fan_speed * 0.02
            self.mock_cabin_temp += (target - self.mock_cabin_temp) * adjustment_rate
        
        return round(self.mock_cabin_temp, 1)
    
    async def _auto_select_mode(self, target_temp: float) -> None:
        """Automatically select appropriate HVAC mode based on target temperature."""
        cabin_temp = await self._get_cabin_temperature()
        
        if target_temp > cabin_temp + 2:
            # Need heating
            await self._apply_mode(HVACMode.HEAT)
        elif target_temp < cabin_temp - 2:
            # Need cooling
            await self._apply_mode(HVACMode.COOL)
        else:
            # Use auto mode
            await self._apply_mode(HVACMode.AUTO)
    
    async def auto_adjust(self) -> None:
        """Perform automatic HVAC adjustments (called periodically)."""
        if not self.auto_mode_enabled:
            return
        
        try:
            cabin_temp = await self._get_cabin_temperature()
            temp_diff = abs(cabin_temp - self.target_temp)
            
            if temp_diff > self.temp_tolerance:
                # Adjust fan speed based on temperature difference
                if temp_diff > 5.0:
                    new_fan_speed = min(6, self.current_state.fan_speed + 1)
                elif temp_diff > 2.0:
                    new_fan_speed = min(4, max(2, self.current_state.fan_speed))
                else:
                    new_fan_speed = max(1, self.current_state.fan_speed - 1)
                
                if new_fan_speed != self.current_state.fan_speed:
                    await self.set_fan_speed(new_fan_speed)
                    self.stats["auto_adjustments"] += 1
                    self.logger.debug(f"🤖 Auto-adjusted fan speed to {new_fan_speed}")
            
        except Exception as e:
            self.logger.error(f"Auto adjustment error: {e}")
    
    def _validate_temperature(self, temp_celsius: float) -> bool:
        """Validate temperature is within safe limits."""
        return self.limits.min_temp <= temp_celsius <= self.limits.max_temp
    
    def _convert_to_celsius(self, temperature: float, unit: str) -> float:
        """Convert temperature to Celsius."""
        if unit.lower() in ["f", "fahrenheit"]:
            return (temperature - 32) * 5 / 9
        return temperature
    
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return celsius * 9 / 5 + 32
    
    def get_stats(self) -> Dict[str, Any]:
        """Get HVAC controller statistics."""
        return self.stats.copy()
    
    async def shutdown(self) -> None:
        """Shutdown HVAC controller."""
        self.logger.info("🛑 Shutting down HVAC Controller...")
        
        # Turn off auto mode
        self.auto_mode_enabled = False
        
        self.logger.info("✅ HVAC Controller shutdown complete")