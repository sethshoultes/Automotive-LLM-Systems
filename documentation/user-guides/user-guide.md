# User Guide

## Getting Started

### First Time Setup

After installation, your Automotive LLM System needs a brief calibration period:

1. **Start your vehicle** and ensure all systems are operational
2. **Wait 30 seconds** for the system to initialize
3. **Listen for the startup confirmation**: "Automotive LLM System started - Listening for commands"
4. **Test basic wake word**: Say "Hey Car" and wait for acknowledgment

### Understanding the System States

The system operates in several states indicated by audio feedback:

- **🟢 Listening**: Ready for wake word detection
- **🔵 Processing**: Wake word detected, listening for command
- **🟡 Thinking**: Processing your command with AI
- **🟠 Speaking**: Providing voice response
- **🔴 Error**: System issue (requires attention)

## Voice Commands Reference

### Wake Words

The system responds to three wake words:

#### "Hey Car" (Primary)
- **Use for**: General vehicle control and status requests
- **Example**: "Hey Car, turn on the air conditioning"

#### "Vehicle Assistant" (Secondary)  
- **Use for**: More formal interactions and system configuration
- **Example**: "Vehicle Assistant, show me engine diagnostics"

#### "Emergency Override" (Critical)
- **Use for**: Emergency situations requiring immediate attention
- **Example**: "Emergency Override, stop all systems"

### Climate Control Commands

#### Temperature Control
```
"Set temperature to [number] degrees"
"Make it warmer" / "Make it cooler"
"Set driver temperature to 72"
"Set passenger temperature to 70"
"Turn on auto mode at 75 degrees"
```

**Supported Temperature Ranges:**
- Celsius: 16°C to 32°C
- Fahrenheit: 60°F to 90°F

#### Fan Control
```
"Turn up the fan"
"Set fan speed to [1-8]"
"Turn off the fan"
"Set fan to maximum"
"Auto fan speed"
```

#### HVAC Modes
```
"Turn on the air conditioning"
"Turn on the heat"
"Switch to auto mode"
"Turn on defrost"
"Activate windshield defroster"
"Switch to vent mode"
```

#### Air Distribution
```
"Direct air to face"
"Direct air to feet"
"Air to face and feet"
"Defrost mode"
```

### Engine Management Commands

#### Performance Monitoring
```
"What's my engine temperature?"
"Check oil pressure"
"What's the current RPM?"
"Show me boost pressure"
"Check fuel economy"
"What's my throttle position?"
```

#### Performance Adjustments (Advanced)
⚠️ **Safety Note**: These commands require confirmation and may affect warranty

```
"Increase boost pressure by [number] PSI"
"Set target boost to [number] PSI"
"Switch to sport mode"
"Enable launch control"
"Reset engine parameters"
```

#### Diagnostic Commands
```
"Check for error codes"
"Clear diagnostic codes"
"Run engine diagnostics"
"Check emissions status"
"Show me engine data"
```

### Lighting Control Commands

#### Interior Lighting
```
"Turn on interior lights"
"Dim lights to [percentage]"
"Set ambient lighting to blue"
"Turn off cabin lights"
"Brighten dashboard"
"Set mood lighting"
```

#### Exterior Lighting
```
"Turn on fog lights"
"Flash hazard lights"
"Turn on parking lights"
"Activate emergency flashers"
```

### Audio System Commands

#### Volume Control
```
"Turn up the volume"
"Set volume to [1-30]"
"Mute audio"
"Unmute speakers"
"Lower the volume"
```

#### Source Control
```
"Switch to radio"
"Change to Bluetooth"
"Switch to USB input"
"Next audio source"
"Play music"
```

#### Playback Control
```
"Skip to next track"
"Previous song"
"Pause music"
"Resume playback"
"Stop audio"
```

### Vehicle Status Commands

#### General Status
```
"What's my vehicle status?"
"Check all systems"
"Show me the dashboard"
"Give me a status report"
"How's everything running?"
```

#### Specific System Status
```
"Check tire pressure"
"What's my fuel level?"
"Show battery voltage"
"Check coolant level"
"What's the outside temperature?"
```

#### Performance Data
```
"What's my current speed?"
"Show me fuel economy"
"What's my average MPG?"
"Check engine load"
"Show me real-time data"
```

### Security and Access Commands

#### Door Control
```
"Lock all doors"
"Unlock driver door"
"Check if doors are locked"
"Open trunk"
"Close all windows"
```

#### Security System
```
"Arm security system"
"Disarm alarm"
"Activate panic mode"
"Check security status"
```

### Emergency Commands

#### Emergency Protocols
```
"Emergency stop all systems"
"Activate emergency mode"
"Override all settings"
"Reset to safe mode"
"Emergency shutdown"
```

#### Safety Alerts
```
"Cancel current operation"
"Stop what you're doing"
"Return to manual control"
"Disable all modifications"
```

## Advanced Features

### Conversation Context

The system remembers recent interactions for natural conversation:

```
User: "Turn on the AC"
System: "Air conditioning is now on"
User: "Make it cooler"
System: "Setting temperature to 70 degrees"
User: "That's perfect"
System: "Temperature locked at 70 degrees"
```

### Multi-Step Commands

Some commands require confirmation for safety:

```
User: "Increase boost pressure by 5 PSI"
System: "This will increase boost to 15 PSI total. This modification may affect your engine warranty and could cause damage if your engine is not properly tuned. Say 'confirm' to proceed."
User: "Confirm"
System: "Boost pressure increased to 15 PSI. Monitoring engine parameters."
```

### Conditional Commands

The system can execute commands based on conditions:

```
"If engine temperature goes above 200 degrees, turn on maximum fan"
"When I stop the car, turn off performance mode"
"If it's raining, turn on the defrost automatically"
```

### Voice Patterns and Natural Language

The system understands various ways to express the same command:

#### Temperature Examples
- "Set temperature to 72"
- "Make it 72 degrees"
- "I want it 72 degrees in here"
- "Can you set the temp to 72?"
- "Turn the heat up to 72"

#### Volume Examples
- "Turn up the volume"
- "Make it louder"
- "Increase audio volume"
- "Can you turn the music up?"
- "Louder please"

## System Responses

### Confirmation Messages
- **Temperature Change**: "Temperature set to 72 degrees"
- **Fan Adjustment**: "Fan speed set to level 5"
- **Mode Change**: "Switched to auto mode"
- **Volume Change**: "Volume set to 15"

### Status Reports
- **Engine Status**: "Engine temperature is 195 degrees, oil pressure is normal"
- **HVAC Status**: "Auto mode active, cabin temperature 73 degrees, fan speed 3"
- **Overall Status**: "All systems operating normally"

### Warning Messages
- **Safety Limits**: "Temperature setting exceeds recommended range"
- **Speed Restrictions**: "Engine modifications not available while driving at highway speeds"
- **System Conflicts**: "Cannot adjust engine parameters while in safe mode"

### Error Messages
- **Command Not Understood**: "I didn't understand that command. Please try again."
- **System Unavailable**: "That system is not available right now"
- **Safety Block**: "I cannot execute that command for safety reasons"

## Customization Options

### Personal Preferences

#### Voice Recognition Training
The system learns your voice patterns over time. For better recognition:
- Speak clearly and at normal volume
- Use consistent phrasing for common commands
- Avoid background noise when possible

#### Custom Temperature Preferences
```
"Remember I like it at 72 degrees"
"Set my preferred temperature to 70"
"Always use auto mode when I start the car"
```

#### Personalized Responses
```
"Call me [name] from now on"
"Use formal responses"
"Keep responses brief"
"Give me detailed explanations"
```

### Vehicle-Specific Settings

#### Performance Profiles
```
"Create sport profile with boost at 12 PSI"
"Save current settings as daily driver mode"
"Switch to track day configuration"
"Load my highway cruising setup"
```

#### System Priorities
```
"Prioritize fuel economy"
"Focus on performance"
"Optimize for comfort"
"Use conservative settings"
```

## Troubleshooting Common Issues

### Voice Recognition Problems

#### System Not Responding to Wake Word
1. Check microphone connection
2. Reduce background noise
3. Speak more clearly
4. Try alternate wake word: "Vehicle Assistant"

#### Commands Not Understood
1. Rephrase using simpler language
2. Use specific numeric values
3. Break complex requests into steps
4. Check if system is in processing mode

### System Response Issues

#### No Audio Response
1. Check audio connections to vehicle
2. Verify volume levels
3. Test with "What's my status?" command
4. Check system logs for audio errors

#### Delayed Responses
1. Wait for processing complete before new command
2. Check system load with status command
3. Verify network connection for LLM
4. Restart system if persistent

### Vehicle Integration Issues

#### OBD-II Data Not Available
1. Ensure vehicle is running or in accessory mode
2. Check OBD-II adapter connection
3. Verify adapter compatibility
4. Try "Check engine diagnostics" command

#### CAN Bus Commands Not Working
1. Verify vehicle-specific protocols
2. Check CAN bus wiring
3. Confirm vehicle compatibility
4. Test with basic lighting commands first

## Safety Guidelines

### Important Safety Rules

1. **Driver Attention**: Always maintain focus on driving
2. **Manual Override**: Keep manual controls accessible
3. **Emergency Stop**: Know how to use "Emergency Override"
4. **Safe Commands**: Avoid complex commands while driving
5. **System Limits**: Respect all safety warnings

### When NOT to Use Voice Commands

- During emergency driving situations
- In heavy traffic requiring full attention
- When learning new roads or routes
- During adverse weather conditions
- When system shows error status

### Best Practices

#### For Safe Operation
- Use simple, clear commands
- Wait for system acknowledgment
- Keep both hands on wheel while speaking
- Use during straight, uncomplicated driving
- Have passenger operate for complex requests

#### For System Longevity
- Regular system health checks
- Keep software updated
- Monitor system logs
- Report unusual behavior
- Follow maintenance schedule

## Getting Help

### Voice Help Commands
```
"What can you do?"
"List available commands"
"Help with climate control"
"Show me engine commands"
"What are the safety rules?"
```

### System Status Commands
```
"Check system health"
"Show me error logs"
"What's wrong with the system?"
"Run diagnostic check"
"Show system statistics"
```

### Support Resources

- **Documentation**: Check `/docs` folder for technical details
- **Logs**: System logs at `/var/log/automotive-llm/`
- **Configuration**: Settings in `config.yaml`
- **Community**: GitHub issues and discussions
- **Updates**: Regular system updates via git

For technical support, collect the following information:
- Voice command that failed
- System response (if any)
- Vehicle make, model, year
- Recent system logs
- Configuration changes made

## What's Next?

### Expanding Functionality
As you become comfortable with basic commands, explore:
- Advanced performance tuning
- Custom voice profiles
- Integration with navigation systems
- Data logging and analysis
- Remote monitoring capabilities

### Learning Resources
- [Developer Guide](developer-guide.md) for customization
- [API Documentation](../api/components.md) for technical details
- [Installation Guide](installation.md) for hardware setup
- Configuration examples in `/examples` folder

The Automotive LLM System is designed to grow with your needs while maintaining safety as the top priority. Enjoy your enhanced driving experience!