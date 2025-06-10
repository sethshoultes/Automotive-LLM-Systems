# Automotive LLM System

> **Local AI assistant for classic cars with voice control and vehicle integration**

Transform your classic car with modern AI technology while preserving its authentic character. This system provides hands-free voice control for vehicle systems using a Raspberry Pi 5, local LLM processing, and direct vehicle integration via OBD-II and CAN bus protocols.

## ✨ **Key Features**

### 🎤 **Natural Voice Control**
- **Wake Word Detection**: "Hey Car", "Vehicle Assistant", "Emergency Override"
- **Natural Language**: Conversational commands like "Make it cooler" or "Turn up the heat to 75"
- **Multi-Turn Conversations**: Context-aware interactions that remember your preferences
- **Real-Time Processing**: <600ms from voice command to vehicle action

```
"Hey Car, set temperature to 72 degrees"
"Turn on the air conditioning"
"What's my engine temperature?"
"Increase boost pressure by 2 PSI"
"Show me this week's performance summary"
```

### 🧠 **Local AI Processing**
- **Privacy First**: All processing on-device, no cloud dependency
- **Ollama Integration**: Local Llama 3.1 8B model with automotive training
- **Hailo Acceleration**: Dedicated AI chip for real-time inference
- **Intent Recognition**: Understands automotive context and vehicle-specific commands

### 🚗 **Complete Vehicle Integration**
- **OBD-II Support**: Read diagnostics from any 1996+ vehicle
- **CAN Bus Control**: Direct control of vehicle systems (make/model specific)
- **Real-Time Monitoring**: Engine temp, RPM, boost pressure, fuel economy
- **Performance Analytics**: Comprehensive data logging and trend analysis

### 🛡️ **Safety-First Design**
- **Multi-Layer Validation**: Intent → Safety → Vehicle → Confirmation pipeline
- **Emergency Protocols**: Immediate safety override with "Emergency Override" command
- **Driver Control**: Manual controls always functional, system cannot override critical safety systems
- **Safety Boundaries**: Clear separation between controllable and critical systems

### 🌡️ **Climate Control**
- **Dual-Zone HVAC**: Independent driver and passenger temperature control
- **Smart Auto Mode**: Learns preferences and adjusts automatically
- **Voice Commands**: "Set temperature to 72", "Turn on defrost", "Auto mode at 75 degrees"
- **Safety Limits**: Temperature and fan speed restrictions for comfort and safety

### 📊 **Performance Monitoring & Analytics**
- **Real-Time Dashboard**: Web interface at localhost:8080 with live vehicle data
- **Session Tracking**: Automatic driving session detection and analysis
- **Data Logging**: Configurable detail levels from minimal to diagnostic
- **Trend Analysis**: Historical performance trends and efficiency monitoring
- **Export Capabilities**: CSV, JSON, and SQLite formats for external analysis

### 🔧 **Engine Management** (Advanced)
- **Performance Tuning**: Boost pressure, timing, and fuel system adjustments
- **Real-Time Monitoring**: Oil pressure, engine load, intake temperatures
- **Safety Validation**: All modifications validated against safety limits
- **Diagnostic Integration**: Read and clear trouble codes via voice commands

## 🎯 **What You Can Control**

### **Climate Systems**
```
Temperature control (16-32°C)    Fan speed (8 levels)
Auto/Heat/Cool/Defrost modes    Air distribution control
Dual-zone support               Automatic adjustments
```

### **Engine Performance**
```
Boost pressure monitoring       RPM and load tracking  
Oil pressure alerts            Fuel economy analysis
Temperature management         Diagnostic code reading
```

### **Lighting & Audio**
```
Interior lighting control      Volume and source control
Brightness adjustment          Playback management
Emergency flashers             Speed-compensated volume
```

### **Vehicle Status**
```
Comprehensive diagnostics      Real-time performance data
Alert management              Historical trend analysis
Export and reporting          Maintenance scheduling
```

## 🏗️ **System Architecture**

### **Hardware Platform**
- **Raspberry Pi 5** (16GB) with Samsung T9 SSD (2TB)
- **Hailo-8 AI Accelerator** for neural processing
- **4-Microphone Array** for 360° voice capture  
- **Vehicle Integration** via OBD-II and CAN bus
- **Automotive Power Management** with 12V integration

### **Software Stack**
- **Voice Processing**: Whisper STT, Piper TTS, Porcupine wake words
- **AI Engine**: Local Ollama with Llama 3.1 8B automotive model
- **Vehicle Protocols**: python-obd, python-can with safety validation
- **Analytics**: SQLite database with FastAPI web dashboard
- **Safety System**: Multi-layer validation with emergency protocols

### **Performance Specifications**
```
Response Time: <600ms total     RAM Usage: ~2GB with models loaded
Voice Accuracy: >95% clean      CPU Usage: <30% during processing  
Voice Accuracy: >85% road noise Storage: ~10GB system + models
System Uptime: >99.5% target    Power: 12V automotive integration
```

## 🚀 **Quick Start**

### **Development Mode** (No Hardware Required)
```bash
# Clone and setup
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run with full simulation
export AUTOMOTIVE_LLM_MOCK_MODE=true
python src/main.py --debug

# Try voice commands:
# "Hey Car, what's my engine temperature?"
# "Set temperature to 72 degrees"
```

### **Analytics Dashboard**
```bash
# Enable web dashboard
export AUTOMOTIVE_LLM_ENABLE_DASHBOARD=true
python src/main.py --debug

# Open browser to http://localhost:8080
# View real-time performance, manage alerts, export data
```

### **Production Installation**
```bash
# On Raspberry Pi 5 with Raspberry Pi OS
sudo apt update && apt install -y python3-pip portaudio19-dev can-utils
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system && python3 -m venv venv
source venv/bin/activate && pip install -r requirements.txt

# Install Ollama and AI model
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b-instruct-q4_K_M

# Configure for your vehicle and run
cp config.yaml config-local.yaml
# Edit config-local.yaml for your vehicle
python src/main.py --config config-local.yaml
```

## 📊 **Analytics & Monitoring**

### **Real-Time Dashboard**
- **System Status**: Live monitoring of all components
- **Performance Metrics**: Engine, thermal, and efficiency data
- **Active Alerts**: Real-time safety and performance warnings
- **Session Tracking**: Automatic driving session analysis

### **Data Collection**
- **Configurable Logging**: Minimal to diagnostic detail levels
- **Multiple Formats**: CSV, JSON, binary, and SQLite export
- **Automatic Compression**: Efficient storage with retention management
- **Historical Analysis**: Performance trends and comparative analysis

### **Voice Analytics Commands**
```
"Show me this week's performance summary"
"Start data logging for this trip"
"Export my driving data from last month"
"Do I have any performance alerts?"
"What's my average fuel economy?"
```

## 🛡️ **Safety & Security**

### **Safety Design**
- **Multi-Stage Validation**: Every command validated through safety pipeline
- **Emergency Override**: Immediate system shutdown with voice command
- **Parameter Limits**: Configurable safety thresholds for all systems
- **Fail-Safe Defaults**: System defaults to safe state on any failure
- **Driver Authority**: Manual controls always functional

### **Security Features**
- **Local Processing**: No cloud dependencies or data transmission
- **Encrypted Storage**: All sensitive data encrypted at rest
- **Access Control**: Multi-level authentication and authorization
- **Audit Logging**: Complete command and action history
- **Physical Security**: Tamper detection and secure enclosure

### **Supported Vehicle Systems**
```
✅ HVAC and climate control        ✅ Engine performance monitoring
✅ Interior/exterior lighting      ✅ Audio and infotainment
✅ Performance parameter tuning    ✅ Diagnostic code management

❌ Braking systems                 ❌ Steering control
❌ Airbag systems                  ❌ Critical safety systems
❌ Transmission shifting           ❌ Suspension control
```

## 📚 **Documentation**

| **For Users** | **For Developers** | **Technical Specs** |
|---------------|-------------------|-------------------|
| [🚀 Getting Started](documentation/getting-started/README.md) | [💻 Developer Guide](documentation/user-guides/developer-guide.md) | [🔧 Hardware Architecture](documentation/technical/hardware-architecture.md) |
| [📖 User Guide](documentation/user-guides/user-guide.md) | [🔍 API Reference](documentation/reference/api/components.md) | [⚙️ Software Architecture](documentation/technical/software-architecture.md) |
| [🔧 Installation Guide](documentation/user-guides/installation.md) | [📊 Current Status](documentation/getting-started/current-status.md) | [🚗 Vehicle Integration](documentation/technical/vehicle-integration.md) |
| [📊 Analytics Guide](documentation/user-guides/analytics-guide.md) | [🧪 Testing Framework](documentation/user-guides/developer-guide.md#testing-framework) | [🛡️ Safety & Security](documentation/technical/safety-security.md) |

**[📚 Complete Documentation Index](documentation/README.md)**

## 🎯 **Project Status**

### ✅ **Fully Implemented**
- Complete voice processing pipeline with wake word detection
- Local LLM integration with automotive-specific training
- Comprehensive vehicle interface (OBD-II + CAN bus)
- Full HVAC control system with safety validation
- Real-time performance monitoring and analytics
- Web dashboard with live data and controls
- Multi-layer safety system with emergency protocols

### 🔧 **Hardware Requirements**
- **Estimated Cost**: ~$640 for complete system
- **Vehicle Compatibility**: Any vehicle with OBD-II port (1996+)
- **Installation**: Professional installation recommended
- **Power**: 12V automotive integration with backup systems

### 🎤 **Voice Commands Working**
Over 50 voice commands implemented across climate control, engine management, lighting, audio, and analytics. Natural language processing with context awareness and multi-turn conversations.

## 🤝 **Community**

### **Contributing**
We welcome contributions from automotive enthusiasts, developers, and classic car owners:
- **Code Contributions**: New features, bug fixes, optimizations
- **Documentation**: Guides, tutorials, vehicle-specific configs
- **Testing**: Hardware testing, vehicle compatibility
- **Community**: Share setups, help other enthusiasts

### **Getting Help**
- **[GitHub Issues](https://github.com/yourusername/automotive-llm-system/issues)**: Bug reports and feature requests
- **[GitHub Discussions](https://github.com/yourusername/automotive-llm-system/discussions)**: Questions and community support
- **[Documentation](documentation/README.md)**: Comprehensive guides and references

## ⚖️ **Legal & Safety**

**Important**: This system is designed for classic cars with aftermarket modifications. Always prioritize safety:

- Driver maintains ultimate control of vehicle
- System cannot override critical safety systems
- Modifications may affect vehicle warranty  
- Comply with local regulations regarding vehicle modifications
- Professional installation recommended for complex integrations
- Thorough testing required before road use

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⚡ Built for automotive enthusiasts who want to bring their classic cars into the AI age while preserving their character and charm.**

**[🚀 Get Started Now](documentation/getting-started/README.md)** | **[📊 View Current Status](documentation/getting-started/current-status.md)** | **[📚 Browse Documentation](documentation/README.md)**