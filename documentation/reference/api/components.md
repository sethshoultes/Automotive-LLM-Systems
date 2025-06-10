# Component API Documentation

## System Controller

The `SystemController` class is the central orchestrator that manages all system components.

### Class: `SystemController`

**Location:** `src/controllers/system_controller.py`

#### Constructor

```python
SystemController(settings: Settings, safety_monitor: SafetyMonitor)
```

**Parameters:**
- `settings`: Configuration settings object
- `safety_monitor`: Safety monitoring system instance

#### Methods

##### `async initialize() -> bool`
Initializes all system components including vehicle interfaces, LLM controller, HVAC controller, and voice manager.

**Returns:** `True` if initialization successful, `False` otherwise

##### `async start() -> None`
Starts the automotive LLM system and begins listening for voice commands.

**Raises:** `RuntimeError` if system not initialized

##### `get_system_status() -> SystemStatus`
Returns current system status including initialization state, component status, and uptime.

**Returns:** `SystemStatus` object with current state

##### `async shutdown() -> None`
Gracefully shuts down all system components.

---

## Voice Manager

Handles voice processing pipeline including wake word detection, speech-to-text, and text-to-speech.

### Class: `VoiceManager`

**Location:** `src/voice/manager.py`

#### Constructor

```python
VoiceManager(config: AudioConfig, command_callback: Callable, keywords: List[str])
```

**Parameters:**
- `config`: Audio configuration settings
- `command_callback`: Function to call when voice command is processed
- `keywords`: List of wake words (default: ["hey-car", "vehicle-assistant", "emergency-override"])

#### Methods

##### `async initialize() -> bool`
Initializes voice processing components and tests audio input.

**Returns:** `True` if successful, `False` otherwise

##### `async start_listening() -> None`
Begins continuous listening for wake words and voice commands.

##### `async speak(text: str) -> None`
Synthesizes and plays text as speech.

**Parameters:**
- `text`: Text to convert to speech

##### `get_stats() -> Dict[str, Any]`
Returns voice processing statistics.

### Class: `WakeWordDetector`

Handles wake word detection using Porcupine or mock implementation.

#### Methods

##### `process_audio(audio_frame: np.ndarray) -> Optional[str]`
Processes audio frame and returns detected wake word if any.

**Parameters:**
- `audio_frame`: Audio data as numpy array

**Returns:** Wake word string if detected, `None` otherwise

### Class: `SpeechToText`

Converts speech to text using Whisper or mock implementation.

#### Methods

##### `async transcribe(audio_data: np.ndarray) -> Tuple[str, float]`
Transcribes audio data to text with confidence score.

**Parameters:**
- `audio_data`: Audio data as numpy array

**Returns:** Tuple of (transcribed_text, confidence_score)

---

## LLM Controller

Manages local language model processing and intent recognition.

### Class: `LLMController`

**Location:** `src/controllers/llm_controller.py`

#### Constructor

```python
LLMController(model_name: str, ollama_host: str)
```

**Parameters:**
- `model_name`: Name of the Ollama model to use (default: "llama3.1:8b-instruct-q4_K_M")
- `ollama_host`: Ollama server URL (default: "http://localhost:11434")

#### Methods

##### `async initialize() -> bool`
Initializes LLM controller and verifies model availability.

##### `async process_command(user_input: str, vehicle_status: Dict) -> LLMResponse`
Processes user command and returns structured response with intent.

**Parameters:**
- `user_input`: Raw text from voice recognition
- `vehicle_status`: Current vehicle state data (optional)

**Returns:** `LLMResponse` object with parsed intent and response text

### Data Classes

#### `Intent`
Represents parsed user intent with entities.

```python
@dataclass
class Intent:
    intent_type: IntentType
    confidence: float
    entities: List[Entity]
    raw_text: str
    action: str
    target: str
    value: Optional[Any] = None
```

#### `LLMResponse`
Response from LLM processing.

```python
@dataclass
class LLMResponse:
    text: str
    intent: Optional[Intent]
    confidence: float
    processing_time: float
    requires_confirmation: bool = False
    safety_warning: Optional[str] = None
```

---

## Vehicle Interface

Provides unified interface for OBD-II and CAN bus communication.

### Class: `VehicleManager`

**Location:** `src/interfaces/vehicle.py`

#### Constructor

```python
VehicleManager(obd_port: str, can_channel: str)
```

**Parameters:**
- `obd_port`: OBD-II port path (default: "/dev/ttyUSB0")
- `can_channel`: CAN interface name (default: "can0")

#### Methods

##### `async initialize() -> bool`
Initializes OBD-II and CAN bus interfaces.

##### `async get_parameter(parameter_name: str) -> Optional[VehicleParameter]`
Retrieves vehicle parameter from appropriate interface.

**Parameters:**
- `parameter_name`: Name of parameter to retrieve

**Returns:** `VehicleParameter` object or `None` if not found

##### `async set_parameter(parameter_name: str, value: Any) -> bool`
Sets vehicle parameter via appropriate interface.

**Parameters:**
- `parameter_name`: Name of parameter to set
- `value`: Value to set

**Returns:** `True` if successful, `False` otherwise

##### `async get_vehicle_status() -> Dict[str, VehicleParameter]`
Returns comprehensive vehicle status including engine parameters.

### Class: `OBDInterface`

Handles OBD-II communication for diagnostic data.

#### Supported Parameters

- `engine_rpm`: Engine RPM
- `vehicle_speed`: Vehicle speed (km/h)
- `engine_temp`: Engine coolant temperature (°C)
- `throttle_pos`: Throttle position (%)
- `fuel_level`: Fuel level (%)
- `intake_temp`: Intake air temperature (°C)
- `maf_rate`: Mass airflow rate (g/s)
- `fuel_pressure`: Fuel rail pressure (kPa)

### Class: `CANInterface`

Handles CAN bus communication for vehicle control.

#### Supported Commands

- `hvac_temp_set`: Set HVAC temperature
- `hvac_fan_speed`: Set fan speed
- `interior_lights`: Control interior lighting
- `audio_volume`: Set audio volume
- `boost_pressure`: Control turbo boost pressure

---

## HVAC Controller

Controls vehicle heating, ventilation, and air conditioning systems.

### Class: `HVACController`

**Location:** `src/controllers/hvac_controller.py`

#### Constructor

```python
HVACController(vehicle_manager: VehicleManager)
```

#### Methods

##### `async set_temperature(temperature: float, zone: str, unit: str) -> Dict[str, Any]`
Sets target temperature for specified zone.

**Parameters:**
- `temperature`: Target temperature value
- `zone`: Zone to control ("driver", "passenger", "both")
- `unit`: Temperature unit ("celsius", "fahrenheit")

**Returns:** Result dictionary with success status and values

##### `async set_fan_speed(speed: int) -> Dict[str, Any]`
Sets fan speed level (0-8).

**Parameters:**
- `speed`: Fan speed level

##### `async set_mode(mode: str) -> Dict[str, Any]`
Sets HVAC operating mode.

**Parameters:**
- `mode`: HVAC mode ("off", "auto", "heat", "cool", "defrost", "vent")

##### `async activate_defrost() -> Dict[str, Any]`
Activates windshield defrost mode.

##### `async get_status() -> Dict[str, Any]`
Returns current HVAC system status.

### Enums

#### `HVACMode`
- `OFF`: System off
- `AUTO`: Automatic temperature control
- `HEAT`: Heating mode
- `COOL`: Cooling mode (AC on)
- `DEFROST`: Windshield defrost
- `VENT`: Ventilation only

#### `FanSpeed`
- `OFF`: Fan off (0)
- `LOW`: Low speed (2)
- `MEDIUM`: Medium speed (4)
- `HIGH`: High speed (6)
- `MAX`: Maximum speed (8)

---

## Safety Monitor

Provides safety validation and monitoring for all vehicle operations.

### Class: `SafetyMonitor`

**Location:** `src/safety/monitor.py`

#### Constructor

```python
SafetyMonitor(settings, vehicle_manager: VehicleManager)
```

#### Methods

##### `async initialize() -> bool`
Initializes safety monitoring system and loads safety rules.

##### `async validate_command(intent_type: str, parameter: str, value: Any, vehicle_state: Dict) -> CommandValidationResult`
Validates if a command is safe to execute.

**Parameters:**
- `intent_type`: Type of command intent
- `parameter`: Target parameter
- `value`: Command value
- `vehicle_state`: Current vehicle state

**Returns:** `CommandValidationResult` with validation outcome

##### `async emergency_protocol() -> None`
Executes emergency safety protocol.

##### `get_safety_status() -> Dict[str, Any]`
Returns current safety system status.

### Data Classes

#### `SafetyRule`
Defines safety limits and actions.

```python
@dataclass
class SafetyRule:
    name: str
    parameter: str
    min_value: Optional[float]
    max_value: Optional[float]
    safety_level: SafetyLevel
    violation_type: SafetyViolationType
    action_required: bool
    description: str
```

#### `CommandValidationResult`
Result of command safety validation.

```python
@dataclass
class CommandValidationResult:
    allowed: bool
    safety_level: SafetyLevel
    warnings: List[str]
    required_confirmations: List[str]
    blocked_reason: Optional[str] = None
```

### Safety Levels

#### `SafetyLevel`
- `SAFE`: Normal operation
- `CAUTION`: Elevated attention required
- `WARNING`: Potentially unsafe conditions
- `CRITICAL`: Immediate action required
- `EMERGENCY`: Emergency protocols activated

---

## Configuration System

Manages system configuration with validation and environment variable support.

### Class: `Settings`

**Location:** `src/config/settings.py`

#### Constructor

```python
Settings(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path`: Path to YAML configuration file (optional)

#### Properties

- `audio`: `AudioSettings` - Audio system configuration
- `vehicle`: `VehicleSettings` - Vehicle interface settings
- `llm`: `LLMSettings` - Language model configuration
- `safety`: `SafetySettings` - Safety system settings
- `hvac`: `HVACSettings` - HVAC system configuration
- `logging`: `LoggingSettings` - Logging configuration
- `system`: `SystemSettings` - System-level settings

#### Methods

##### `save_config(path: Optional[str] = None) -> bool`
Saves current configuration to YAML file.

##### `validate_config() -> List[str]`
Validates configuration and returns list of errors.

##### `get_config_summary() -> Dict[str, Any]`
Returns configuration summary for logging.

### Configuration Classes

#### `AudioSettings`
```python
sample_rate: int = 16000
channels: int = 1
chunk_size: int = 1024
input_device_index: Optional[int] = None
wake_word_sensitivity: float = 0.7
noise_reduction: bool = True
```

#### `VehicleSettings`
```python
obd_port: str = "/dev/ttyUSB0"
obd_baudrate: int = 38400
can_channel: str = "can0"
can_bitrate: int = 500000
enable_obd: bool = True
enable_can: bool = True
vehicle_make: str = "generic"
vehicle_model: str = "unknown"
vehicle_year: int = 2000
```

#### `LLMSettings`
```python
model_name: str = "llama3.1:8b-instruct-q4_K_M"
ollama_host: str = "http://localhost:11434"
max_tokens: int = 512
temperature: float = 0.7
context_window: int = 4096
enable_hailo: bool = True
```

---

## Error Handling

All components implement comprehensive error handling:

### Exception Types

- **`RuntimeError`**: System not properly initialized
- **`ValueError`**: Invalid parameter values or configurations
- **`ConnectionError`**: Vehicle interface communication failures
- **`SafetyViolationError`**: Safety rule violations

### Graceful Degradation

Components implement fallback modes:

- **Voice Manager**: Falls back to mock mode if hardware unavailable
- **Vehicle Interface**: Continues with available interfaces
- **LLM Controller**: Uses mock responses if Ollama unavailable
- **Safety Monitor**: Defaults to restrictive safety mode

### Logging

All components use structured logging with:

- **DEBUG**: Detailed operation information
- **INFO**: General operational messages
- **WARNING**: Potential issues that don't stop operation
- **ERROR**: Errors that affect functionality
- **CRITICAL**: Critical failures requiring immediate attention

---

## Performance Considerations

### Memory Usage

- **Base system**: ~300MB RAM
- **With LLM loaded**: ~2GB RAM (8B model)
- **Voice buffers**: ~50MB for audio processing
- **Vehicle data cache**: ~10MB

### Processing Times

- **Wake word detection**: <100ms
- **Speech recognition**: <200ms
- **LLM processing**: 100-500ms (depending on Hailo acceleration)
- **Vehicle command execution**: <100ms
- **Total voice-to-action**: <600ms target

### Optimization Features

- **Async/await**: Non-blocking operations throughout
- **Hailo acceleration**: Hardware AI acceleration for inference
- **Audio preprocessing**: Noise reduction and VAD
- **Caching**: Vehicle state and LLM context caching
- **Mock modes**: Development without hardware dependencies