# Documentation Index

## 📚 **Complete Documentation Guide**

Welcome to the Automotive LLM System documentation! This guide will help you find exactly what you need.

## 🚀 **Getting Started**

**New to the project?** Start here:

- **[Quick Start Guide](getting-started/README.md)** - Get running in 5 minutes
- **[Current Status](getting-started/current-status.md)** - What's implemented and working
- **[Project Overview](../README.md)** - Features and capabilities

## 👥 **User Documentation**

**Using the system?** These guides are for you:

### Installation & Setup
- **[Installation Guide](user-guides/installation.md)** - Complete hardware and software setup
  - Hardware requirements and wiring
  - Raspberry Pi configuration
  - Vehicle integration steps
  - Testing and validation

### Daily Usage
- **[User Guide](user-guides/user-guide.md)** - Voice commands and system operation
  - Voice command reference
  - System operation and safety
  - Customization options
  - Troubleshooting common issues

- **[Analytics Guide](user-guides/analytics-guide.md)** - Performance monitoring and data analysis
  - Performance monitoring setup
  - Data logging configuration
  - Web dashboard usage
  - Data export and analysis

## 💻 **Developer Documentation**

**Contributing or customizing?** These are your resources:

- **[Developer Guide](user-guides/developer-guide.md)** - Development environment and contributing
  - Development setup
  - Architecture overview
  - Creating new components
  - Testing and contribution guidelines

- **[API Reference](reference/api/components.md)** - Complete component APIs
  - All class and method documentation
  - Integration examples
  - Error handling patterns

## 🔧 **Technical Specifications**

**Need technical details?** Deep dive documentation:

### System Architecture
- **[Software Architecture](technical/software-architecture.md)** - System design and components
- **[Hardware Architecture](technical/hardware-architecture.md)** - Hardware specifications and requirements

### Integration Details  
- **[Vehicle Integration](technical/vehicle-integration.md)** - OBD-II and CAN bus protocols
- **[Voice Interface](technical/voice-interface.md)** - Voice processing design
- **[System Controls](technical/system-controls.md)** - Vehicle system control mapping

### Safety & Development
- **[Safety & Security](technical/safety-security.md)** - Safety protocols and security measures
- **[Development Roadmap](technical/development-roadmap.md)** - Development timeline and testing

## 📖 **Quick Reference**

### Most Common Tasks

| Task | Documentation |
|------|---------------|
| **Get started quickly** | [Getting Started Guide](getting-started/README.md) |
| **Install on Raspberry Pi** | [Installation Guide](user-guides/installation.md) |
| **Learn voice commands** | [User Guide](user-guides/user-guide.md#voice-commands-reference) |
| **Set up analytics** | [Analytics Guide](user-guides/analytics-guide.md) |
| **Develop features** | [Developer Guide](user-guides/developer-guide.md) |
| **API reference** | [Component APIs](reference/api/components.md) |
| **Safety information** | [Safety & Security](technical/safety-security.md) |

### Quick Start Commands

```bash
# Development mode (no hardware)
export AUTOMOTIVE_LLM_MOCK_MODE=true
python src/main.py --debug

# With analytics dashboard
export AUTOMOTIVE_LLM_ENABLE_DASHBOARD=true
python src/main.py --debug
# Open http://localhost:8080

# Production mode
python src/main.py --config config.yaml
```

### Voice Commands Quick Reference

```
"Hey Car, set temperature to 72 degrees"
"Turn on the air conditioning"
"What's my engine temperature?"
"Show me this week's performance summary"
"Start data logging"
"Export my driving data"
"Emergency stop all systems"
```

## 🎯 **Documentation by Role**

### **Classic Car Enthusiast**
You want to add modern AI to your classic car:
1. [Project Overview](../README.md) - Understand what this system does
2. [Hardware Architecture](technical/hardware-architecture.md) - What you need to buy
3. [Installation Guide](user-guides/installation.md) - How to install it
4. [User Guide](user-guides/user-guide.md) - How to use it safely

### **Developer**
You want to contribute or customize:
1. [Getting Started](getting-started/README.md) - Quick development setup
2. [Current Status](getting-started/current-status.md) - What's already done
3. [Developer Guide](user-guides/developer-guide.md) - How to contribute
4. [API Reference](reference/api/components.md) - Technical details

### **System Integrator**
You're installing this professionally:
1. [Safety & Security](technical/safety-security.md) - Critical safety information
2. [Installation Guide](user-guides/installation.md) - Professional installation
3. [Vehicle Integration](technical/vehicle-integration.md) - Technical integration details
4. [Analytics Guide](user-guides/analytics-guide.md) - Monitoring and maintenance

### **Researcher/Student**
You're studying AI in automotive applications:
1. [Software Architecture](technical/software-architecture.md) - System design
2. [Voice Interface](technical/voice-interface.md) - Voice processing techniques
3. [Development Roadmap](technical/development-roadmap.md) - Implementation methodology
4. [API Reference](reference/api/components.md) - Implementation details

## 🛟 **Getting Help**

### **Support Channels**
- **Issues**: [GitHub Issues](https://github.com/yourusername/automotive-llm-system/issues) - Bug reports and feature requests
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/automotive-llm-system/discussions) - Questions and community help
- **Documentation**: Browse this documentation for comprehensive information

### **Common Questions**

**Q: Can I run this without a car?**
A: Yes! Use mock mode: `export AUTOMOTIVE_LLM_MOCK_MODE=true`

**Q: What vehicles are supported?**
A: Any vehicle with OBD-II port (1996+ in US). CAN bus support varies by make/model.

**Q: Is this safe to install?**
A: Yes, with proper installation. The system cannot control critical safety systems. Read [Safety & Security](technical/safety-security.md) first.

**Q: How much does it cost?**
A: Approximately $640 for complete hardware setup. See [Hardware Architecture](technical/hardware-architecture.md).

**Q: Can I contribute?**
A: Absolutely! See [Developer Guide](user-guides/developer-guide.md) for contribution guidelines.

## 📊 **Documentation Status**

| Document | Status | Last Updated |
|----------|--------|--------------|
| Getting Started | ✅ Complete | Current |
| User Guides | ✅ Complete | Current |
| Technical Specs | ✅ Complete | Current |
| API Reference | ✅ Complete | Current |
| Developer Guide | ✅ Complete | Current |

All documentation is current and reflects the latest implementation.

---

**Need something specific?** Use the search function in your browser (Ctrl+F / Cmd+F) or check the [GitHub repository](https://github.com/yourusername/automotive-llm-system) for the latest updates.