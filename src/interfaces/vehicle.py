"""
Vehicle Interface - OBD-II and CAN bus communication
"""

import logging
import time
import can
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union, Any

try:
    import obd
    OBD_AVAILABLE = True
except ImportError:
    OBD_AVAILABLE = False
    logging.warning("python-obd not available - using mock OBD interface")


class VehicleSystemType(Enum):
    """Types of vehicle systems."""
    ENGINE = "engine"
    TRANSMISSION = "transmission"
    HVAC = "hvac"
    LIGHTING = "lighting"
    SECURITY = "security"
    AUDIO = "audio"


@dataclass
class VehicleParameter:
    """Represents a vehicle parameter with metadata."""
    name: str
    value: Union[float, int, str, bool]
    unit: str
    timestamp: float
    system_type: VehicleSystemType
    source: str  # "obd", "can", "gpio"


@dataclass
class CANMessage:
    """Represents a CAN bus message."""
    arbitration_id: int
    data: bytes
    timestamp: float
    is_extended_id: bool = False


class VehicleInterface(ABC):
    """Abstract base class for vehicle interfaces."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the vehicle."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the vehicle."""
        pass
    
    @abstractmethod
    async def get_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get a specific vehicle parameter."""
        pass
    
    @abstractmethod
    async def set_parameter(self, parameter_name: str, value: Any) -> bool:
        """Set a vehicle parameter."""
        pass


class OBDInterface(VehicleInterface):
    """OBD-II interface for reading vehicle diagnostics."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 38400):
        self.port = port
        self.baudrate = baudrate
        self.connection: Optional[obd.OBD] = None
        self.logger = logging.getLogger(__name__)
        self.mock_mode = not OBD_AVAILABLE
        
        # OBD-II PIDs we can read
        self.supported_pids = {
            "engine_rpm": obd.commands.RPM if OBD_AVAILABLE else None,
            "vehicle_speed": obd.commands.SPEED if OBD_AVAILABLE else None,
            "engine_temp": obd.commands.COOLANT_TEMP if OBD_AVAILABLE else None,
            "throttle_pos": obd.commands.THROTTLE_POS if OBD_AVAILABLE else None,
            "fuel_level": obd.commands.FUEL_LEVEL if OBD_AVAILABLE else None,
            "intake_temp": obd.commands.INTAKE_TEMP if OBD_AVAILABLE else None,
            "maf_rate": obd.commands.MAF if OBD_AVAILABLE else None,
            "fuel_pressure": obd.commands.FUEL_PRESSURE if OBD_AVAILABLE else None,
        }
        
        # Mock data for development
        self.mock_data = {
            "engine_rpm": 850.0,
            "vehicle_speed": 0.0,
            "engine_temp": 95.0,
            "throttle_pos": 0.0,
            "fuel_level": 78.5,
            "intake_temp": 25.0,
            "maf_rate": 2.5,
            "fuel_pressure": 350.0,
        }
    
    async def connect(self) -> bool:
        """Connect to OBD-II interface."""
        if self.mock_mode:
            self.logger.warning("🔧 Using mock OBD interface")
            return True
        
        try:
            self.connection = obd.OBD(self.port, baudrate=self.baudrate)
            
            if self.connection.status() == obd.OBDStatus.CAR_CONNECTED:
                self.logger.info(f"✅ OBD-II connected on {self.port}")
                return True
            else:
                self.logger.error(f"❌ OBD-II connection failed: {self.connection.status()}")
                return False
                
        except Exception as e:
            self.logger.error(f"OBD-II connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from OBD-II interface."""
        if self.connection and not self.mock_mode:
            self.connection.close()
            self.connection = None
        self.logger.info("🔌 OBD-II disconnected")
    
    async def get_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get OBD-II parameter."""
        if self.mock_mode:
            return self._get_mock_parameter(parameter_name)
        
        if not self.connection or parameter_name not in self.supported_pids:
            return None
        
        try:
            cmd = self.supported_pids[parameter_name]
            response = self.connection.query(cmd)
            
            if response.value is not None:
                return VehicleParameter(
                    name=parameter_name,
                    value=float(response.value.magnitude) if hasattr(response.value, 'magnitude') else response.value,
                    unit=str(response.value.units) if hasattr(response.value, 'units') else "",
                    timestamp=time.time(),
                    system_type=VehicleSystemType.ENGINE,
                    source="obd"
                )
        except Exception as e:
            self.logger.error(f"Error reading OBD parameter {parameter_name}: {e}")
        
        return None
    
    def _get_mock_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get mock parameter data for development."""
        if parameter_name in self.mock_data:
            # Add some variation to mock data
            base_value = self.mock_data[parameter_name]
            variation = base_value * 0.05  # 5% variation
            import random
            value = base_value + random.uniform(-variation, variation)
            
            units_map = {
                "engine_rpm": "rpm",
                "vehicle_speed": "km/h",
                "engine_temp": "°C",
                "throttle_pos": "%",
                "fuel_level": "%",
                "intake_temp": "°C",
                "maf_rate": "g/s",
                "fuel_pressure": "kPa"
            }
            
            return VehicleParameter(
                name=parameter_name,
                value=round(value, 1),
                unit=units_map.get(parameter_name, ""),
                timestamp=time.time(),
                system_type=VehicleSystemType.ENGINE,
                source="obd"
            )
        return None
    
    async def set_parameter(self, parameter_name: str, value: Any) -> bool:
        """OBD-II is read-only, cannot set parameters."""
        self.logger.warning(f"Cannot set OBD-II parameter {parameter_name}: read-only interface")
        return False
    
    async def get_diagnostic_codes(self) -> List[str]:
        """Get diagnostic trouble codes."""
        if self.mock_mode:
            return []  # No mock DTCs
        
        if not self.connection:
            return []
        
        try:
            response = self.connection.query(obd.commands.GET_DTC)
            if response.value:
                return [str(code) for code in response.value]
        except Exception as e:
            self.logger.error(f"Error reading DTCs: {e}")
        
        return []


class CANInterface(VehicleInterface):
    """CAN bus interface for advanced vehicle control."""
    
    def __init__(self, channel: str = "can0", bitrate: int = 500000):
        self.channel = channel
        self.bitrate = bitrate
        self.bus: Optional[can.Bus] = None
        self.logger = logging.getLogger(__name__)
        self.mock_mode = True  # Start in mock mode until CAN is detected
        
        # Vehicle-specific CAN message definitions
        self.message_definitions = {
            # HVAC Control Messages
            "hvac_temp_set": {"id": 0x3F1, "dlc": 8},
            "hvac_fan_speed": {"id": 0x3F2, "dlc": 8},
            "hvac_mode": {"id": 0x3F3, "dlc": 8},
            
            # Lighting Control Messages  
            "interior_lights": {"id": 0x4A1, "dlc": 8},
            "exterior_lights": {"id": 0x4A2, "dlc": 8},
            
            # Engine Management
            "boost_pressure": {"id": 0x201, "dlc": 8},
            "fuel_trim": {"id": 0x202, "dlc": 8},
            
            # Audio System
            "audio_volume": {"id": 0x5B1, "dlc": 8},
            "audio_source": {"id": 0x5B2, "dlc": 8},
        }
        
        # Current vehicle state cache
        self.vehicle_state = {}
    
    async def connect(self) -> bool:
        """Connect to CAN bus."""
        try:
            # Try to initialize CAN interface
            self.bus = can.Bus(
                channel=self.channel,
                bustype='socketcan',
                bitrate=self.bitrate
            )
            
            # Test if we can send a message
            test_msg = can.Message(
                arbitration_id=0x123,
                data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            
            self.bus.send(test_msg, timeout=1.0)
            self.mock_mode = False
            self.logger.info(f"✅ CAN bus connected on {self.channel}")
            return True
            
        except Exception as e:
            self.logger.warning(f"CAN bus not available, using mock mode: {e}")
            self.mock_mode = True
            return True  # Return True for mock mode
    
    async def disconnect(self) -> None:
        """Disconnect from CAN bus."""
        if self.bus and not self.mock_mode:
            self.bus.shutdown()
            self.bus = None
        self.logger.info("🔌 CAN bus disconnected")
    
    async def get_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get parameter from CAN bus or cache."""
        if parameter_name in self.vehicle_state:
            cached_value = self.vehicle_state[parameter_name]
            return VehicleParameter(
                name=parameter_name,
                value=cached_value["value"],
                unit=cached_value.get("unit", ""),
                timestamp=cached_value["timestamp"],
                system_type=self._get_system_type(parameter_name),
                source="can"
            )
        return None
    
    async def set_parameter(self, parameter_name: str, value: Any) -> bool:
        """Set vehicle parameter via CAN bus."""
        if parameter_name not in self.message_definitions:
            self.logger.error(f"Unknown CAN parameter: {parameter_name}")
            return False
        
        msg_def = self.message_definitions[parameter_name]
        
        try:
            # Create CAN message based on parameter
            data = self._encode_parameter(parameter_name, value)
            
            message = can.Message(
                arbitration_id=msg_def["id"],
                data=data,
                is_extended_id=False
            )
            
            if self.mock_mode:
                # Simulate successful transmission
                self.logger.info(f"🔧 Mock CAN: Set {parameter_name} = {value}")
                self._update_vehicle_state(parameter_name, value)
                return True
            else:
                # Send actual CAN message
                self.bus.send(message, timeout=1.0)
                self.logger.info(f"📡 CAN message sent: {parameter_name} = {value}")
                self._update_vehicle_state(parameter_name, value)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set CAN parameter {parameter_name}: {e}")
            return False
    
    def _encode_parameter(self, parameter_name: str, value: Any) -> bytes:
        """Encode parameter value into CAN message data."""
        # This would contain vehicle-specific encoding logic
        data = [0x00] * 8  # Initialize 8-byte array
        
        if parameter_name == "hvac_temp_set":
            # Temperature in Celsius, offset by 40, scale by 2
            temp_encoded = int((float(value) + 40) * 2)
            data[0] = temp_encoded & 0xFF
        
        elif parameter_name == "hvac_fan_speed":
            # Fan speed 0-8
            data[0] = int(value) & 0xFF
        
        elif parameter_name == "interior_lights":
            # Brightness percentage 0-100
            data[0] = int(value) & 0xFF
        
        elif parameter_name == "audio_volume":
            # Volume level 0-30
            data[0] = int(value) & 0xFF
        
        elif parameter_name == "boost_pressure":
            # Boost pressure in 0.1 PSI units
            pressure_encoded = int(float(value) * 10)
            data[0] = pressure_encoded & 0xFF
            data[1] = (pressure_encoded >> 8) & 0xFF
        
        return bytes(data)
    
    def _update_vehicle_state(self, parameter_name: str, value: Any) -> None:
        """Update cached vehicle state."""
        unit_map = {
            "hvac_temp_set": "°C",
            "hvac_fan_speed": "level",
            "interior_lights": "%",
            "audio_volume": "level",
            "boost_pressure": "PSI"
        }
        
        self.vehicle_state[parameter_name] = {
            "value": value,
            "unit": unit_map.get(parameter_name, ""),
            "timestamp": time.time()
        }
    
    def _get_system_type(self, parameter_name: str) -> VehicleSystemType:
        """Get system type for parameter."""
        if parameter_name.startswith("hvac_"):
            return VehicleSystemType.HVAC
        elif parameter_name.startswith("audio_"):
            return VehicleSystemType.AUDIO
        elif "lights" in parameter_name:
            return VehicleSystemType.LIGHTING
        elif parameter_name in ["boost_pressure", "fuel_trim"]:
            return VehicleSystemType.ENGINE
        else:
            return VehicleSystemType.ENGINE
    
    async def listen_for_messages(self, timeout: float = 1.0) -> List[CANMessage]:
        """Listen for incoming CAN messages."""
        if self.mock_mode:
            return []  # No mock messages for now
        
        if not self.bus:
            return []
        
        messages = []
        try:
            message = self.bus.recv(timeout=timeout)
            if message:
                can_msg = CANMessage(
                    arbitration_id=message.arbitration_id,
                    data=message.data,
                    timestamp=message.timestamp,
                    is_extended_id=message.is_extended_id
                )
                messages.append(can_msg)
        except Exception as e:
            self.logger.debug(f"CAN message receive timeout or error: {e}")
        
        return messages


class VehicleManager:
    """Unified vehicle interface manager."""
    
    def __init__(self, obd_port: str = "/dev/ttyUSB0", can_channel: str = "can0"):
        self.logger = logging.getLogger(__name__)
        
        # Initialize interfaces
        self.obd = OBDInterface(port=obd_port)
        self.can = CANInterface(channel=can_channel)
        
        # Connection status
        self.obd_connected = False
        self.can_connected = False
        
        # Combined vehicle state
        self.vehicle_parameters = {}
    
    async def initialize(self) -> bool:
        """Initialize all vehicle interfaces."""
        self.logger.info("🚗 Initializing Vehicle Manager...")
        
        # Try to connect to OBD-II
        self.obd_connected = await self.obd.connect()
        if self.obd_connected:
            self.logger.info("✅ OBD-II interface ready")
        
        # Try to connect to CAN bus
        self.can_connected = await self.can.connect()
        if self.can_connected:
            self.logger.info("✅ CAN bus interface ready")
        
        if self.obd_connected or self.can_connected:
            self.logger.info("✅ Vehicle Manager initialized")
            return True
        else:
            self.logger.error("❌ No vehicle interfaces available")
            return False
    
    async def get_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get parameter from appropriate interface."""
        # Try OBD first for engine parameters
        if self.obd_connected:
            param = await self.obd.get_parameter(parameter_name)
            if param:
                return param
        
        # Try CAN for control parameters
        if self.can_connected:
            param = await self.can.get_parameter(parameter_name)
            if param:
                return param
        
        return None
    
    async def set_parameter(self, parameter_name: str, value: Any) -> bool:
        """Set parameter via appropriate interface."""
        # Most set operations go through CAN
        if self.can_connected:
            return await self.can.set_parameter(parameter_name, value)
        
        self.logger.warning(f"Cannot set parameter {parameter_name}: no writable interface available")
        return False
    
    async def get_vehicle_status(self) -> Dict[str, VehicleParameter]:
        """Get comprehensive vehicle status."""
        status = {}
        
        # Common OBD parameters
        obd_params = [
            "engine_rpm", "vehicle_speed", "engine_temp", 
            "throttle_pos", "fuel_level", "intake_temp"
        ]
        
        for param in obd_params:
            value = await self.get_parameter(param)
            if value:
                status[param] = value
        
        return status
    
    async def get_diagnostic_codes(self) -> List[str]:
        """Get diagnostic trouble codes."""
        if self.obd_connected:
            return await self.obd.get_diagnostic_codes()
        return []
    
    async def shutdown(self) -> None:
        """Shutdown all vehicle interfaces."""
        self.logger.info("🛑 Shutting down Vehicle Manager...")
        
        if self.obd_connected:
            await self.obd.disconnect()
        
        if self.can_connected:
            await self.can.disconnect()
        
        self.logger.info("✅ Vehicle Manager shutdown complete")