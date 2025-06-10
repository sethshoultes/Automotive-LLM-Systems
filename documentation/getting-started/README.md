# Getting Started with Automotive LLM System

Welcome to the Automotive LLM System! This guide will help you get up and running quickly, whether you're looking to develop, test, or deploy the system.

## Quick Start Options

### 🚀 **Option 1: Development Mode (No Hardware)**
Perfect for developers, testing, and exploring features without any automotive hardware.

```bash
# Clone and setup
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode with all mocks enabled
export AUTOMOTIVE_LLM_MOCK_MODE=true
python src/main.py --debug

# The system will start with simulated vehicle data
# Try voice commands like "Hey Car, what's my engine temperature?"
```

### 🔧 **Option 2: Raspberry Pi Setup (Production)**
For actual vehicle installation with Raspberry Pi 5 hardware.

```bash
# On Raspberry Pi 5 with Raspberry Pi OS
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv portaudio19-dev can-utils

# Enable hardware interfaces
sudo raspi-config
# Enable: SPI, I2C, Serial, SSH

# Clone and setup project
git clone https://github.com/yourusername/automotive-llm-system.git
cd automotive-llm-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Ollama for local LLM
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b-instruct-q4_K_M

# Configure for your vehicle
cp config.yaml config-local.yaml
nano config-local.yaml  # Edit vehicle settings

# Run system
python src/main.py --config config-local.yaml
```

### 🌐 **Option 3: Analytics Dashboard Only**
Just want to see the dashboard and analytics features?

```bash
# Quick setup
pip install -r requirements.txt

# Start with analytics dashboard enabled
export AUTOMOTIVE_LLM_MOCK_MODE=true
export AUTOMOTIVE_LLM_ENABLE_DASHBOARD=true
python src/main.py --debug

# Open browser to http://localhost:8080
```

## What's Included

### ✅ **Working Components**
- **Voice Processing**: Complete pipeline with wake word detection, STT, TTS
- **LLM Integration**: Local Ollama integration with automotive prompts
- **Vehicle Interface**: OBD-II and CAN bus communication (with mocks)
- **Safety System**: Multi-layer validation and emergency protocols
- **HVAC Control**: Complete climate control system
- **Analytics System**: Performance monitoring, data logging, web dashboard
- **Configuration**: Comprehensive settings management

### 🎤 **Voice Commands You Can Try**
```
"Hey Car, set temperature to 72 degrees"
"Turn on the air conditioning"
"What's my engine temperature?"
"Show me this week's performance summary"
"Start data logging"
"Do I have any alerts?"
```

### 📊 **Dashboard Features**
- Real-time system status
- Performance metrics and trends
- Active alert management
- Data logging controls
- Export functionality

## Your First Session

### 1. **Start the System**
```bash
# Development mode
export AUTOMOTIVE_LLM_MOCK_MODE=true
python src/main.py --debug
```

Expected output:
```
🚗 Initializing Automotive LLM System...
✅ Safety Monitor initialized with 7 rules
✅ Vehicle Manager initialized
🧠 LLM Controller initialized (mock mode)
🌡️ HVAC Controller initialized  
🎤 Voice Manager initialized
✅ System initialization complete
🎤 Automotive LLM System started - Listening for commands...
```

### 2. **Try Voice Commands**
Wait for the "Listening for commands" message, then try:
- "Hey Car, what's my status?"
- "Set temperature to 72 degrees"
- "Turn on the air conditioning"

### 3. **Access the Dashboard** (Optional)
If dashboard is enabled:
- Open browser to http://localhost:8080
- View real-time system status
- Start/stop data logging
- View performance metrics

### 4. **Check the Logs**
```bash
# View system logs
tail -f /var/log/automotive-llm/system.log

# Or check console output for debug info
```

## Next Steps

### For Developers
1. **Read the [Developer Guide](../user-guides/developer-guide.md)**
2. **Explore the [API Documentation](../reference/api/components.md)**
3. **Check out example code in the codebase**
4. **Run tests**: `pytest tests/`

### For Vehicle Installation
1. **Follow the [Installation Guide](../user-guides/installation.md)**
2. **Review [Hardware Architecture](../technical/hardware-architecture.md)**
3. **Understand [Safety Protocols](../technical/safety-security.md)**
4. **Configure for your vehicle make/model**

### For Users
1. **Read the [User Guide](../user-guides/user-guide.md)**
2. **Learn [Voice Commands](../user-guides/user-guide.md#voice-commands-reference)**
3. **Explore [Analytics Features](../user-guides/analytics-guide.md)**

## Troubleshooting Quick Fixes

### System Won't Start
```bash
# Check Python version (need 3.11+)
python --version

# Check virtual environment is activated
which python

# Install missing dependencies
pip install -r requirements.txt

# Check for permission issues
sudo chown -R $USER:$USER .
```

### Voice Commands Not Working
```bash
# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -d 5 test.wav && aplay test.wav

# Check mock mode is enabled for development
export AUTOMOTIVE_LLM_MOCK_MODE=true
```

### Dashboard Not Loading
```bash
# Install web dependencies
pip install fastapi uvicorn

# Check if port 8080 is available
netstat -tulpn | grep 8080

# Try different port
python src/main.py --debug --dashboard-port 8081
```

### OBD-II Issues (Hardware Mode)
```bash
# Check USB connection
ls /dev/ttyUSB*

# Test ELM327 adapter
screen /dev/ttyUSB0 38400

# Check vehicle is in accessory mode or running
```

## System Requirements

### Development Environment
- **Python**: 3.11 or higher
- **OS**: Linux, macOS, or Windows (Linux preferred)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB for system + models

### Production Environment (Raspberry Pi)
- **Raspberry Pi 5**: 16GB RAM model recommended
- **Display**: 10.1" capacitive touch screen for Raspberry Pi
- **Storage**: Samsung T9 SSD (2TB) or equivalent
- **Audio**: 4-microphone USB array
- **Vehicle**: OBD-II port (1996+ vehicles in US)
- **Power**: 12V automotive power management system

## Support and Resources

### Documentation Structure
```
documentation/
├── getting-started/           # This guide
├── user-guides/              # User documentation
│   ├── installation.md       # Hardware setup
│   ├── user-guide.md        # Voice commands & usage
│   ├── analytics-guide.md   # Performance monitoring
│   └── developer-guide.md   # Development & contributing
├── technical/               # Technical specifications
│   ├── hardware-architecture.md
│   ├── software-architecture.md
│   ├── vehicle-integration.md
│   ├── safety-security.md
│   └── system-controls.md
└── reference/              # API reference
    └── api/
        └── components.md   # Complete API documentation
```

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/automotive-llm-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/automotive-llm-system/discussions)
- **Documentation**: Browse the `documentation/` directory
- **Examples**: Check `docs/examples/` for code samples

### Community
- Share your classic car setup and modifications
- Contribute improvements and new features
- Help other enthusiasts with their installations
- Report bugs and suggest enhancements

---

## What's Next?

Choose your path:

🔧 **Want to install in your vehicle?**
→ [Installation Guide](../user-guides/installation.md)

💻 **Want to contribute code?**
→ [Developer Guide](../user-guides/developer-guide.md)

🎤 **Want to learn voice commands?**
→ [User Guide](../user-guides/user-guide.md)

📊 **Want to explore analytics?**
→ [Analytics Guide](../user-guides/analytics-guide.md)

🔍 **Want technical details?**
→ [Technical Documentation](../technical/)

Welcome to the future of classic car technology! 🚗✨