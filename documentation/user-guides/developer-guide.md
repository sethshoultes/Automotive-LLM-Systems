# Developer Guide

## Architecture Overview

The Automotive LLM System is built with a modular, event-driven architecture designed for real-time automotive applications. The system emphasizes safety, reliability, and extensibility.

### Core Design Principles

1. **Safety First**: Multiple validation layers prevent unsafe operations
2. **Modularity**: Components can be developed and tested independently
3. **Async/Await**: Non-blocking operations for real-time performance
4. **Mock Development**: Full functionality without hardware dependencies
5. **Graceful Degradation**: System continues operating with failed components

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Main Controller                       │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐   │
│  │ Voice Mgr   │ │ LLM Control  │ │ Safety Monitor  │   │
│  └─────────────┘ └──────────────┘ └─────────────────┘   │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐   │
│  │ HVAC Ctrl   │ │ Vehicle Mgr  │ │ Config System   │   │
│  └─────────────┘ └──────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                    ┌─────────────┐
                    │  Hardware   │
                    │ OBD │ CAN   │
                    │ MIC │ GPIO  │
                    └─────────────┘
```

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Git
- Virtual environment capability
- IDE with Python support (VS Code recommended)

### Development Setup

#### 1. Clone and Setup Environment
```bash
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

#### 2. Development Dependencies
Create `requirements-dev.txt`:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.0.0
mypy>=1.5.0
pre-commit>=3.3.0
pytest-mock>=3.11.0
```

#### 3. Pre-commit Hooks
```bash
pre-commit install
```

#### 4. IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Mock Development Mode

All components support mock mode for development without hardware:

```python
# Environment variables for mock mode
export AUTOMOTIVE_LLM_MOCK_MODE=true
export AUTOMOTIVE_LLM_OBD_MOCK=true
export AUTOMOTIVE_LLM_CAN_MOCK=true
export AUTOMOTIVE_LLM_VOICE_MOCK=true
```

## Component Development

### Creating New Controllers

#### 1. Controller Base Structure
```python
# src/controllers/example_controller.py
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ExampleState:
    """State data for the example controller."""
    active: bool = False
    value: float = 0.0
    timestamp: float = 0.0

class ExampleController:
    """Example controller template."""
    
    def __init__(self, vehicle_manager):
        self.vehicle_manager = vehicle_manager
        self.logger = logging.getLogger(__name__)
        self.state = ExampleState()
        self.stats = {"commands_executed": 0}
    
    async def initialize(self) -> bool:
        """Initialize the controller."""
        try:
            self.logger.info("🔧 Initializing Example Controller...")
            # Initialization logic here
            self.logger.info("✅ Example Controller initialized")
            return True
        except Exception as e:
            self.logger.error(f"Example Controller initialization failed: {e}")
            return False
    
    async def execute_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a controller command."""
        try:
            # Command execution logic
            self.stats["commands_executed"] += 1
            return {"success": True, "result": "Command executed"}
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current controller status."""
        return {
            "state": self.state.__dict__,
            "stats": self.stats.copy()
        }
    
    async def shutdown(self) -> None:
        """Shutdown the controller."""
        self.logger.info("🛑 Shutting down Example Controller...")
        # Cleanup logic here
        self.logger.info("✅ Example Controller shutdown complete")
```

#### 2. Integration with System Controller

Add to `SystemController._execute_command()`:
```python
elif intent.intent_type.value == "example_control":
    return await self._execute_example_command(intent)
```

Add command handler:
```python
async def _execute_example_command(self, intent) -> bool:
    """Execute example controller commands."""
    if not self.example_controller:
        return False
    
    result = await self.example_controller.execute_command(
        intent.action, 
        {"target": intent.target, "value": intent.value}
    )
    return result.get("success", False)
```

### Adding Vehicle Interfaces

#### 1. New Interface Implementation
```python
# src/interfaces/custom_interface.py
from interfaces.vehicle import VehicleInterface, VehicleParameter

class CustomInterface(VehicleInterface):
    """Custom vehicle interface implementation."""
    
    def __init__(self, config_params):
        self.config = config_params
        self.connected = False
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Connect to custom interface."""
        try:
            # Connection logic here
            self.connected = True
            self.logger.info("✅ Custom interface connected")
            return True
        except Exception as e:
            self.logger.error(f"Custom interface connection failed: {e}")
            return False
    
    async def get_parameter(self, parameter_name: str) -> Optional[VehicleParameter]:
        """Get parameter from custom interface."""
        if not self.connected:
            return None
        
        # Parameter retrieval logic
        return VehicleParameter(
            name=parameter_name,
            value=0.0,  # Actual value
            unit="unit",
            timestamp=time.time(),
            system_type=VehicleSystemType.ENGINE,
            source="custom"
        )
    
    async def set_parameter(self, parameter_name: str, value: Any) -> bool:
        """Set parameter via custom interface."""
        if not self.connected:
            return False
        
        # Parameter setting logic
        return True
```

#### 2. Integration with Vehicle Manager
```python
# In VehicleManager.__init__()
self.custom_interface = CustomInterface(custom_config)

# In VehicleManager.initialize()
custom_connected = await self.custom_interface.connect()
if custom_connected:
    self.logger.info("✅ Custom interface ready")
```

### Extending LLM Capabilities

#### 1. Custom Intent Types
```python
# Add to controllers/llm_controller.py
class IntentType(Enum):
    # Existing intents...
    CUSTOM_CONTROL = "custom_control"
    NAVIGATION = "navigation"
    DIAGNOSTICS = "diagnostics"
```

#### 2. Custom Prompt Templates
```python
CUSTOM_SYSTEM_PROMPT = """You are specialized in [specific domain].

Your capabilities:
- Custom function 1
- Custom function 2

Respond with JSON containing:
- "intent": the intent type
- "custom_field": domain-specific data
"""

# Add to LLMController
def _get_system_prompt(self, domain: str) -> str:
    """Get domain-specific system prompt."""
    if domain == "custom":
        return CUSTOM_SYSTEM_PROMPT
    return AutomotivePromptTemplate.SYSTEM_PROMPT
```

#### 3. Custom Entity Extraction
```python
def extract_custom_entities(self, text: str) -> List[Entity]:
    """Extract domain-specific entities."""
    entities = []
    
    # Custom extraction logic
    # Example: Extract coordinates, addresses, etc.
    
    return entities
```

### Safety System Extensions

#### 1. Custom Safety Rules
```python
# Add to safety/monitor.py
def _initialize_custom_safety_rules(self) -> List[SafetyRule]:
    """Initialize custom safety rules."""
    return [
        SafetyRule(
            name="custom_parameter_limit",
            parameter="custom_param",
            min_value=0.0,
            max_value=100.0,
            safety_level=SafetyLevel.WARNING,
            violation_type=SafetyViolationType.SYSTEM_INTEGRITY,
            action_required=False,
            description="Custom parameter out of range"
        )
    ]
```

#### 2. Custom Validation Logic
```python
async def validate_custom_command(self, command_data: Dict[str, Any]) -> CommandValidationResult:
    """Custom command validation logic."""
    
    # Domain-specific validation
    if command_data.get("risk_level", 0) > 5:
        return CommandValidationResult(
            allowed=False,
            safety_level=SafetyLevel.CRITICAL,
            warnings=[],
            required_confirmations=[],
            blocked_reason="Risk level too high"
        )
    
    return CommandValidationResult(
        allowed=True,
        safety_level=SafetyLevel.SAFE,
        warnings=[],
        required_confirmations=[]
    )
```

## Testing Framework

### Unit Testing

#### 1. Test Structure
```
tests/
├── unit/
│   ├── test_voice_manager.py
│   ├── test_llm_controller.py
│   ├── test_vehicle_interface.py
│   ├── test_hvac_controller.py
│   └── test_safety_monitor.py
├── integration/
│   ├── test_system_integration.py
│   └── test_voice_to_action.py
├── fixtures/
│   ├── audio_samples/
│   └── vehicle_data/
└── conftest.py
```

#### 2. Example Unit Test
```python
# tests/unit/test_hvac_controller.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from controllers.hvac_controller import HVACController, HVACMode

@pytest.fixture
def mock_vehicle_manager():
    """Mock vehicle manager for testing."""
    mock = Mock()
    mock.get_parameter = AsyncMock(return_value=None)
    mock.set_parameter = AsyncMock(return_value=True)
    return mock

@pytest.fixture
async def hvac_controller(mock_vehicle_manager):
    """HVAC controller fixture."""
    controller = HVACController(mock_vehicle_manager)
    await controller.initialize()
    return controller

@pytest.mark.asyncio
async def test_set_temperature_celsius(hvac_controller):
    """Test setting temperature in Celsius."""
    result = await hvac_controller.set_temperature(22.0, "both", "celsius")
    
    assert result["success"] is True
    assert result["temperature_celsius"] == 22.0
    assert result["temperature_fahrenheit"] == 71.6

@pytest.mark.asyncio
async def test_temperature_limits(hvac_controller):
    """Test temperature limit enforcement."""
    # Test upper limit
    result = await hvac_controller.set_temperature(50.0, "both", "celsius")
    assert result["success"] is False
    assert "outside safe range" in result["error"]
    
    # Test lower limit
    result = await hvac_controller.set_temperature(10.0, "both", "celsius")
    assert result["success"] is False

@pytest.mark.asyncio
async def test_fan_speed_control(hvac_controller):
    """Test fan speed control."""
    result = await hvac_controller.set_fan_speed(5)
    
    assert result["success"] is True
    assert result["fan_speed"] == 5
```

#### 3. Integration Testing
```python
# tests/integration/test_voice_to_action.py
import pytest
from src.main import AutomotiveLLMSystem

@pytest.mark.asyncio
async def test_voice_command_pipeline():
    """Test complete voice command pipeline."""
    
    # Setup system in mock mode
    system = AutomotiveLLMSystem()
    system.settings.mock_mode = True
    
    assert await system.initialize()
    
    # Simulate voice command
    await system._handle_voice_command(
        VoiceCommand(
            text="set temperature to 72 degrees",
            confidence=0.95,
            timestamp=time.time(),
            wake_word="hey-car",
            processing_time=0.2
        )
    )
    
    # Verify system state
    hvac_status = await system.hvac_controller.get_status()
    assert hvac_status["driver_temp_celsius"] == 22.2  # 72°F in Celsius
```

### Mock Testing Utilities

#### 1. Mock Vehicle Data
```python
# tests/fixtures/mock_vehicle.py
class MockVehicleData:
    """Provides realistic mock vehicle data."""
    
    @staticmethod
    def get_engine_parameters():
        return {
            "engine_rpm": 850.0,
            "engine_temp": 95.0,
            "oil_pressure": 45.0,
            "throttle_pos": 0.0
        }
    
    @staticmethod
    def get_hvac_status():
        return {
            "driver_temp": 22.0,
            "fan_speed": 3,
            "mode": "auto"
        }
```

#### 2. Audio Testing
```python
# tests/fixtures/audio_helpers.py
import numpy as np

def generate_test_audio(duration: float, sample_rate: int = 16000) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Generate simple sine wave
    frequency = 440  # A4 note
    return np.sin(2 * np.pi * frequency * t).astype(np.float32)

def load_test_wake_word() -> np.ndarray:
    """Load pre-recorded wake word for testing."""
    # In real implementation, would load actual audio file
    return generate_test_audio(1.0)  # 1 second of test audio
```

## Configuration and Deployment

### Configuration Management

#### 1. Environment-Specific Configs
```
config/
├── development.yaml
├── testing.yaml
├── production.yaml
└── vehicle-profiles/
    ├── ford-mustang-1970.yaml
    ├── chevrolet-camaro-1969.yaml
    └── generic-classic.yaml
```

#### 2. Vehicle Profile Example
```yaml
# config/vehicle-profiles/ford-mustang-1970.yaml
vehicle:
  make: "ford"
  model: "mustang"
  year: 1970
  engine_type: "v8"
  
safety:
  max_boost_pressure: 8.0  # Conservative for classic engine
  engine_temp_warning: 100.0
  engine_temp_critical: 105.0
  max_rpm: 6000.0

hvac:
  # Classic car may not have advanced HVAC
  min_temperature: 18.0
  max_temperature: 30.0
  max_fan_speed: 4
  dual_zone: false

can_messages:
  # Vehicle-specific CAN message definitions
  hvac_temp_set:
    id: 0x3F1
    dlc: 8
    encoding: "temp_celsius_offset_40_scale_2"
```

#### 3. Dynamic Configuration Loading
```python
def load_vehicle_profile(make: str, model: str, year: int) -> Dict[str, Any]:
    """Load vehicle-specific configuration."""
    profile_name = f"{make}-{model}-{year}.yaml"
    profile_path = f"config/vehicle-profiles/{profile_name}"
    
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Fallback to generic profile
    with open("config/vehicle-profiles/generic-classic.yaml", 'r') as f:
        return yaml.safe_load(f)
```

### Deployment Strategies

#### 1. Development Deployment
```bash
# Quick development start
python src/main.py --debug --config config/development.yaml
```

#### 2. Production Deployment
```bash
# Systemd service for production
sudo systemctl start automotive-llm.service
sudo systemctl enable automotive-llm.service
```

#### 3. Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    can-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY config.yaml .

CMD ["python", "src/main.py"]
```

## Contributing Guidelines

### Code Style

#### 1. Python Style Guide
- Follow PEP 8
- Use Black for formatting
- Maximum line length: 88 characters
- Use type hints for all functions
- Document all public methods

#### 2. Naming Conventions
```python
# Classes: PascalCase
class VehicleManager:

# Functions and methods: snake_case
def get_engine_temperature():

# Constants: UPPER_CASE
MAX_BOOST_PRESSURE = 20.0

# Private methods: _leading_underscore
def _internal_method():
```

#### 3. Documentation Standards
```python
def calculate_fuel_economy(distance: float, fuel_used: float) -> float:
    """Calculate fuel economy in miles per gallon.
    
    Args:
        distance: Distance traveled in miles
        fuel_used: Fuel consumed in gallons
        
    Returns:
        Fuel economy in miles per gallon
        
    Raises:
        ValueError: If fuel_used is zero or negative
    """
    if fuel_used <= 0:
        raise ValueError("Fuel used must be positive")
    return distance / fuel_used
```

### Git Workflow

#### 1. Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates

#### 2. Commit Messages
```
type(scope): Short description

Longer description if needed

- Bullet points for multiple changes
- Reference issues: Fixes #123

Co-authored-by: Name <email>
```

#### 3. Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Create pull request with description
6. Address review feedback
7. Merge after approval

### Security Considerations

#### 1. Code Security
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all external inputs
- Implement proper error handling

#### 2. Vehicle Safety
- Always implement safety checks
- Test thoroughly before vehicle integration
- Document all safety assumptions
- Review changes affecting vehicle control

#### 3. Data Privacy
- Minimize data collection
- Encrypt sensitive data
- Provide data deletion capabilities
- Document data handling practices

## Performance Optimization

### Profiling and Monitoring

#### 1. Performance Monitoring
```python
import time
import psutil
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    cpu_usage: float
    memory_usage: float
    response_time: float
    
async def monitor_performance():
    """Monitor system performance metrics."""
    start_time = time.time()
    
    # Your code here
    
    response_time = time.time() - start_time
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    return PerformanceMetrics(cpu_usage, memory_usage, response_time)
```

#### 2. Async Optimization
```python
# Good: Concurrent operations
async def process_multiple_commands(commands):
    tasks = [process_command(cmd) for cmd in commands]
    results = await asyncio.gather(*tasks)
    return results

# Bad: Sequential operations
async def process_multiple_commands_slow(commands):
    results = []
    for cmd in commands:
        result = await process_command(cmd)
        results.append(result)
    return results
```

### Memory Management

#### 1. Resource Cleanup
```python
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for resource in self.resources:
            await resource.cleanup()
```

#### 2. Memory Monitoring
```python
def monitor_memory_usage():
    """Monitor and log memory usage."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    logging.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
    
    if memory_info.rss > 1024 * 1024 * 1024:  # 1GB
        logging.warning("High memory usage detected")
```

## Debugging and Troubleshooting

### Logging Strategy

#### 1. Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "Command executed",
    command_type="temperature_set",
    target_temp=72,
    zone="driver",
    processing_time=0.156
)
```

#### 2. Debug Mode
```python
# Enable debug logging
logging.getLogger().setLevel(logging.DEBUG)

# Add performance timing
@functools.wraps(func)
def timed_execution(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper
```

### Common Issues and Solutions

#### 1. Async/Await Issues
```python
# Problem: Blocking operations in async functions
def bad_async_function():
    time.sleep(1)  # Blocks event loop
    
# Solution: Use async alternatives
async def good_async_function():
    await asyncio.sleep(1)  # Non-blocking
```

#### 2. Memory Leaks
```python
# Problem: Unclosed resources
stream = await create_stream()
# ... use stream
# Missing: await stream.close()

# Solution: Use context managers
async with create_stream() as stream:
    # ... use stream
    pass  # Automatically closed
```

This developer guide provides the foundation for extending and maintaining the Automotive LLM System. Always prioritize safety and testing when making changes that affect vehicle control systems.