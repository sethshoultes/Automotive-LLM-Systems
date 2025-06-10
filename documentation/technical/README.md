# Automotive LLM System

A comprehensive local AI assistant system for classic cars with modern computer integration. This system provides hands-free voice control for vehicle systems using a Raspberry Pi 5, local LLM processing, and direct vehicle integration via OBD-II and CAN bus protocols.

## 🚗 Overview

This project enables classic car owners to add modern AI-powered voice control to their vehicles while maintaining the authentic driving experience. The system operates entirely offline using local LLM processing for privacy and reliability.

### Key Features

- **Local AI Processing**: No cloud dependency, all processing on-device
- **Voice Control**: Natural language commands for vehicle systems
- **Vehicle Integration**: Direct control via OBD-II and CAN bus protocols
- **Safety First**: Multiple validation layers and fail-safe mechanisms
- **Hands-Free Operation**: Designed for safe use while driving
- **Customizable**: Adaptable to different vehicle makes and models

## 🔧 Hardware Requirements

### Core Components
- **Raspberry Pi 5 (16GB RAM)** - Main computing platform
- **Samsung T9 Portable SSD (2TB)** - High-speed storage for models
- **Hailo-8 AI Accelerator** - Neural processing acceleration
- **4-Microphone USB Array** - 360-degree voice capture
- **Pi Camera Module 3** - Driver monitoring and cabin awareness

### Vehicle Integration
- **ELM327 OBD-II Adapter** - Basic diagnostic access
- **MCP2515 CAN Controller** - Advanced vehicle system control
- **12V Power Management System** - Automotive power integration
- **Relay Modules** - Vehicle system switching
- **Environmental Enclosure** - IP54 rated protection

**Estimated Total Cost: ~$640**

## 💻 Software Architecture

### AI Stack
- **Ollama** - Local LLM serving platform
- **Llama 3.1 8B Instruct** - Primary language model
- **Whisper (Base)** - Speech-to-text processing
- **Piper TTS** - Text-to-speech synthesis
- **Picovoice Porcupine** - Wake word detection

### Vehicle Integration
- **Python-OBD** - OBD-II protocol handling
- **Python-CAN** - CAN bus communication
- **Custom Controllers** - HVAC, lighting, engine management
- **Safety Monitoring** - Real-time system validation

### Performance Targets
- **Response Time**: < 600ms total (wake-to-response)
- **Voice Accuracy**: > 95% in clean conditions
- **Voice Accuracy**: > 85% with road noise
- **System Uptime**: > 99.5%

## 🛡️ Safety & Security

### Safety Features
- Multi-stage command validation
- Safety parameter enforcement
- Emergency override protocols
- Driver attention monitoring
- Fail-safe system defaults

### Security Features
- Local-only processing (no cloud data)
- Multi-factor authentication
- Encrypted data storage
- Network intrusion detection
- Physical tamper protection

## 🎯 Controllable Systems

### Climate Control
- Temperature adjustment (driver/passenger zones)
- Fan speed control
- Mode selection (heat/cool/auto/defrost)
- Air distribution control

### Engine Management
- Performance parameter monitoring
- Boost pressure control (turbo/supercharged)
- Fuel system optimization
- Diagnostic code reading

### Lighting Systems
- Interior lighting (brightness/color)
- Exterior lighting control
- Ambient lighting customization
- Emergency flasher activation

### Audio & Infotainment
- Volume and source control
- Playback management
- Equalizer adjustment
- Speed-compensated volume

## 🗣️ Voice Commands

```
"Hey Car, set temperature to 72 degrees"
"Turn on the air conditioning"
"What's my engine temperature?"
"Increase boost pressure by 2 PSI"
"Dim interior lights to 50 percent"
"Play some music"
"Lock all doors"
"Emergency - activate panic alarm"
```

## 🏗️ Implementation Status

### ✅ Completed Components

#### Core System
- **Main Controller** (`src/main.py`) - Complete system orchestration
- **System Controller** (`src/controllers/system_controller.py`) - Central coordination
- **Configuration System** (`src/config/settings.py`) - Full settings management

#### Voice Processing
- **Voice Manager** (`src/voice/manager.py`) - Complete voice pipeline
- **Wake Word Detection** - Porcupine integration with mock fallback
- **Speech Recognition** - Whisper integration with mock mode
- **Text-to-Speech** - Piper TTS integration

#### AI and Language Model
- **LLM Controller** (`src/controllers/llm_controller.py`) - Ollama integration
- **Intent Recognition** - Automotive-specific intent parsing
- **Conversation Management** - Context and history tracking
- **Safety-aware Responses** - Command validation integration

#### Vehicle Integration
- **Vehicle Manager** (`src/interfaces/vehicle.py`) - Unified interface
- **OBD-II Interface** - Diagnostic data reading with python-obd
- **CAN Bus Interface** - Vehicle control with python-can
- **Mock Modes** - Full development without hardware

#### Vehicle Controllers
- **HVAC Controller** (`src/controllers/hvac_controller.py`) - Complete climate control
- **Temperature Management** - Dual-zone support with safety limits
- **Fan Control** - 8-speed control with auto mode
- **Mode Selection** - Heat/cool/auto/defrost modes

#### Safety System
- **Safety Monitor** (`src/safety/monitor.py`) - Comprehensive safety validation
- **Multi-level Safety Rules** - Engine, HVAC, performance limits
- **Command Validation** - Real-time safety checking
- **Emergency Protocols** - Fail-safe mechanisms

### 🔧 Key Implementation Features

#### Async Architecture
- **Non-blocking Operations** - Full async/await implementation
- **Concurrent Processing** - Parallel voice, vehicle, and AI operations
- **Real-time Performance** - <600ms voice-to-action pipeline

#### Mock Development System
- **Hardware Independence** - Full functionality without vehicle/hardware
- **Realistic Simulation** - Mock vehicle data and responses
- **Development Friendly** - Easy testing and iteration

#### Safety-First Design
- **Multi-stage Validation** - Intent → Safety → Vehicle → Confirmation
- **Emergency Override** - Immediate safety protocol activation
- **Graceful Degradation** - System continues with failed components

#### Vehicle Integration
- **Protocol Support** - OBD-II and CAN bus protocols
- **Vehicle Agnostic** - Configurable for different makes/models
- **Safety Boundaries** - Clear separation of safe vs critical systems

## 📁 Project Structure

```
automotive-llm-system/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── config.yaml                         # System configuration
├── src/
│   ├── main.py                        # Main entry point
│   ├── controllers/
│   │   ├── system_controller.py       # Central orchestration
│   │   ├── llm_controller.py          # AI processing
│   │   └── hvac_controller.py         # Climate control
│   ├── interfaces/
│   │   └── vehicle.py                 # OBD-II & CAN integration
│   ├── voice/
│   │   └── manager.py                 # Voice processing pipeline
│   ├── safety/
│   │   └── monitor.py                 # Safety validation system
│   └── config/
│       └── settings.py                # Configuration management
├── docs/
│   ├── api/
│   │   └── components.md              # API documentation
│   └── guides/
│       ├── installation.md            # Hardware & software setup
│       ├── user-guide.md              # Voice commands reference
│       └── developer-guide.md         # Development guidelines
├── hardware-architecture.md           # Hardware specifications
├── software-architecture.md           # Software design details
├── vehicle-integration.md             # Vehicle protocols
├── safety-security.md                # Safety protocols
├── voice-interface.md                 # Voice processing design
├── system-controls.md                 # Vehicle control mapping
└── development-roadmap.md             # Development timeline
```

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi 5 with 16GB RAM
- Compatible vehicle with OBD-II port (1996+ in US)
- Python 3.11+ development experience

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure system (edit as needed)
cp config.yaml.example config.yaml
nano config.yaml
```

### Development Mode (No Hardware Required)
```bash
# Run in development mode with mocks
export AUTOMOTIVE_LLM_MOCK_MODE=true
python src/main.py --debug
```

### Production Setup
```bash
# Configure hardware interfaces
sudo raspi-config
# Enable SPI, I2C, and GPIO interfaces

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b-instruct-q4_K_M

# Install Hailo runtime (Raspberry Pi)
# See docs/guides/installation.md for details

# Run system
python src/main.py --config config.yaml
```

### Testing Voice Commands
Once running, try these commands:
```
"Hey Car, what's my engine temperature?"
"Turn on the air conditioning"
"Set temperature to 72 degrees"
"What's my vehicle status?"
```

## 📚 Documentation

### User Documentation
- **[Installation Guide](docs/guides/installation.md)** - Complete hardware and software setup
- **[User Guide](docs/guides/user-guide.md)** - Voice commands and system operation
- **[Voice Commands Reference](docs/guides/user-guide.md#voice-commands-reference)** - Complete command list

### Technical Documentation
- **[API Documentation](docs/api/components.md)** - Component APIs and interfaces
- **[Developer Guide](docs/guides/developer-guide.md)** - Development and contribution guidelines
- **[Architecture Documents](software-architecture.md)** - System design details

### Hardware Documentation
- **[Hardware Architecture](hardware-architecture.md)** - Component specifications
- **[Vehicle Integration](vehicle-integration.md)** - OBD-II and CAN bus protocols
- **[Safety & Security](safety-security.md)** - Safety protocols and security measures

## 🔧 Development Features

### Mock Development Mode
Develop and test without any automotive hardware:
```python
# All components support mock mode
voice_manager = VoiceManager(config, mock_mode=True)
vehicle_manager = VehicleManager(mock_mode=True)
llm_controller = LLMController(mock_mode=True)
```

### Comprehensive Testing
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

### Live Development
```bash
# Watch for changes and restart
python src/main.py --debug --watch

# View real-time logs
tail -f /var/log/automotive-llm/system.log
```

## 🛡️ Safety Implementation

### Multi-Layer Safety Validation
1. **Intent Validation** - Command understanding and context
2. **Safety Rules** - Parameter limits and operational constraints
3. **Vehicle State** - Real-time vehicle condition checking
4. **User Confirmation** - Required for safety-critical operations
5. **Emergency Override** - Immediate system safety protocols

### Example Safety Flow
```
User: "Increase boost pressure by 5 PSI"
│
├─ Intent Recognition ✓
├─ Safety Validation ⚠️  (High boost pressure detected)
├─ Confirmation Required: "This will increase boost to 15 PSI total. 
│                         Confirm this is safe for your engine."
├─ User: "Confirm"
├─ Final Safety Check ✓
└─ Execute Command ✓
```

## 🎯 Performance Characteristics

### Real-Time Performance
- **Wake Word Detection**: <100ms
- **Speech Recognition**: <200ms  
- **LLM Processing**: 100-500ms (with Hailo acceleration)
- **Vehicle Command**: <100ms
- **Total Pipeline**: <600ms target

### Resource Usage
- **Base System**: ~300MB RAM
- **With LLM Loaded**: ~2GB RAM (8B model)
- **CPU Usage**: <30% during processing
- **Storage**: ~10GB for system + models

## ⚠️ Legal and Safety Disclaimer

**IMPORTANT**: This system is designed for classic cars with aftermarket modifications. Always prioritize safety:

- Driver maintains ultimate control of vehicle
- System cannot override critical safety systems (brakes, steering, airbags)
- Modifications may affect vehicle warranty
- Comply with local regulations regarding vehicle modifications
- Professional installation recommended for complex integrations
- Thorough testing required before road use

## 🤝 Contributing

We welcome contributions to improve the system:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow safety-first design principles
- Include comprehensive tests
- Document all changes
- Maintain backward compatibility
- See [Developer Guide](docs/guides/developer-guide.md) for details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper speech recognition
- Meta for Llama language models
- Raspberry Pi Foundation for the computing platform
- Automotive open-source community for protocols and libraries

## 📧 Support

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/automotive-llm-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/automotive-llm-system/discussions)
- **Documentation**: Review the `docs/` directory
- **Email**: For security issues only

## 🔗 Quick Links

- **[🚀 Quick Start](#quick-start)** - Get running in minutes
- **[📖 Installation Guide](docs/guides/installation.md)** - Complete setup instructions
- **[🎤 Voice Commands](docs/guides/user-guide.md#voice-commands-reference)** - What you can say
- **[🔧 Developer Guide](docs/guides/developer-guide.md)** - Contribute to the project
- **[🛡️ Safety Guide](safety-security.md)** - Safety protocols and considerations

---

**⚡ Built for automotive enthusiasts who want to bring their classic cars into the AI age while preserving their character and charm.**