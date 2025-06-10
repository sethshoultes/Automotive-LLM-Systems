# Installation and Setup Guide

## Prerequisites

### Hardware Requirements

#### Raspberry Pi 5 Setup
- **Raspberry Pi 5 (16GB RAM)** - Main computing platform
- **10.1" capacitive touch screen** for Raspberry Pi - Primary dashboard display
- **Samsung T9 Portable SSD (2TB)** - High-speed external storage
- **Hailo-8 AI Accelerator** - Neural processing acceleration
- **High-quality microSD card** (64GB+ Class 10) for OS
- **Reliable power supply** (5V/5A USB-C)

#### Audio Hardware
- **4-microphone USB array** (ReSpeaker 4-Mic Array recommended)
- **3.5mm audio cable** to vehicle audio system
- **USB audio adapter** (optional, for better audio quality)

#### Vehicle Integration Hardware
- **ELM327 OBD-II adapter** (USB connection)
- **MCP2515 CAN controller** with SPI interface
- **CAN transceiver** (MCP2562 or similar)
- **12V to 5V power converter** (automotive grade)
- **Relay modules** (8-channel, 12V automotive relays)
- **Environmental enclosure** (IP54 rated)

#### Tools Required
- Soldering iron and solder
- Multimeter
- Wire strippers and crimpers
- Drill and drill bits
- Mounting hardware

### Software Prerequisites

#### Raspberry Pi OS
- **Raspberry Pi OS (64-bit)** - Latest version
- **Python 3.11+** (included with recent Pi OS)
- **Git** (for code deployment)

#### System Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1-dev \
    can-utils \
    i2c-tools \
    spi-tools \
    git \
    curl \
    wget
```

## Step 1: Hardware Setup

### 1.1 Raspberry Pi Configuration

#### Enable Required Interfaces
```bash
sudo raspi-config
```

Navigate to **Interface Options** and enable:
- SPI (for CAN controller)
- I2C (for sensors)
- Serial Port (for debugging)
- SSH (for remote access)

#### Configure Boot from SSD
1. Connect Samsung T9 SSD via USB 3.0
2. Use Raspberry Pi Imager to write OS to SSD
3. Update bootloader to prefer USB boot:
```bash
sudo rpi-eeprom-config --edit
# Change BOOT_ORDER=0xf25641 (USB first, then SD)
sudo reboot
```

### 1.2 Audio Setup

#### Connect Microphone Array
1. Connect ReSpeaker 4-Mic Array via USB
2. Verify detection:
```bash
lsusb | grep -i audio
arecord -l
```

#### Test Audio Input
```bash
# Record test audio
arecord -D plughw:1,0 -f cd test.wav -d 5

# Play back to verify
aplay test.wav
```

#### Configure Audio Output
```bash
# List audio devices
aplay -l

# Set default output (example for 3.5mm jack)
sudo nano /etc/asound.conf
```

Add to `/etc/asound.conf`:
```
pcm.!default {
    type hw
    card 0
    device 0
}
```

### 1.3 Vehicle Interface Wiring

#### OBD-II Connection
1. Connect ELM327 adapter to vehicle's OBD-II port
2. Connect adapter to Raspberry Pi via USB
3. Verify connection:
```bash
ls /dev/ttyUSB*
# Should show /dev/ttyUSB0
```

#### CAN Bus Wiring
**MCP2515 to Raspberry Pi 5:**
```
MCP2515    Raspberry Pi 5    GPIO Pin
VCC    ->  3.3V          ->  Pin 1
GND    ->  GND           ->  Pin 6
CS     ->  GPIO 8 (CE0)  ->  Pin 24
SO     ->  GPIO 9 (MISO) ->  Pin 21
SI     ->  GPIO 10 (MOSI)->  Pin 19
SCK    ->  GPIO 11 (SCLK)->  Pin 23
INT    ->  GPIO 25       ->  Pin 22
```

**CAN Transceiver Connections:**
```
MCP2562    CAN Bus
CANH   ->  CAN High (Vehicle)
CANL   ->  CAN Low (Vehicle)
VDD    ->  5V (from vehicle)
VSS    ->  Ground (vehicle chassis)
```

#### Power System Wiring
**⚠️ SAFETY WARNING: Work with vehicle power OFF**

1. **12V Input:**
   - Connect to vehicle's accessory power (ignition-switched)
   - Add 10A fuse for protection
   - Use automotive-grade wire (14-16 AWG)

2. **Power Converter:**
   - Install 12V to 5V/5A DC-DC converter
   - Mount in ventilated location
   - Add output filtering capacitors

3. **Relay Control:**
   - Connect relay module to Pi GPIO
   - Use optoisolated relays for safety
   - Ground all relay coils to Pi ground

### 1.4 Physical Installation

#### Enclosure Setup
1. Mount Raspberry Pi in IP54 enclosure
2. Install cooling fan with temperature control
3. Add desiccant packs for moisture control
4. Ensure all cables have strain relief

#### Vehicle Mounting
1. Choose location away from heat sources
2. Secure with vibration-dampening mounts
3. Ensure access to connectors for maintenance
4. Route cables away from moving parts

## Step 2: Software Installation

### 2.1 System Preparation

#### Create Project Directory
```bash
sudo mkdir -p /opt/automotive-llm
sudo chown pi:pi /opt/automotive-llm
cd /opt/automotive-llm
```

#### Clone Repository
```bash
git clone https://github.com/yourusername/automotive-llm-system.git .
```

#### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Python Dependencies

#### Install Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Install Hardware-Specific Packages
```bash
# For Raspberry Pi GPIO
pip install RPi.GPIO gpiozero

# For CAN bus support
sudo apt install can-utils
pip install python-can

# For OBD-II support
pip install python-obd

# For audio processing
pip install pyaudio sounddevice
```

### 2.3 CAN Bus Configuration

#### Enable CAN Interface
```bash
sudo nano /etc/modules
```

Add these lines:
```
mcp251x
can
can_raw
```

#### Configure CAN Interface
```bash
sudo nano /etc/systemd/network/80-can.network
```

Add:
```ini
[Match]
Name=can0

[CAN]
BitRate=500000
RestartSec=100ms
```

#### Create CAN Setup Script
```bash
sudo nano /etc/systemd/system/can-setup.service
```

Add:
```ini
[Unit]
Description=Setup CAN interface
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/ip link set can0 up type can bitrate 500000
RemainAfterExit=true
ExecStop=/bin/ip link set can0 down
StandardOutput=journal

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable can-setup.service
```

### 2.4 Ollama Installation

#### Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Download Language Model
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
```

#### Verify Installation
```bash
ollama list
ollama serve
```

### 2.5 Hailo AI Setup

#### Install Hailo Runtime
```bash
# Download Hailo runtime for Raspberry Pi
wget https://hailo.ai/downloads/raspberry-pi/hailo-rpi-runtime.deb
sudo dpkg -i hailo-rpi-runtime.deb
sudo apt-get install -f
```

#### Configure Hailo Service
```bash
sudo systemctl enable hailo-service
sudo systemctl start hailo-service
```

#### Verify Hailo Installation
```bash
hailortcli fw-control identify
```

## Step 3: Configuration

### 3.1 System Configuration

#### Copy Configuration File
```bash
cp config.yaml.example config.yaml
```

#### Edit Configuration
```bash
nano config.yaml
```

**Key settings to update:**
```yaml
vehicle:
  vehicle_make: "your_make"      # e.g., "ford", "chevrolet"
  vehicle_model: "your_model"    # e.g., "mustang", "camaro"
  vehicle_year: 1970             # Your vehicle's year
  obd_port: "/dev/ttyUSB0"       # Verify correct port
  can_channel: "can0"            # CAN interface name

audio:
  input_device_index: 1          # Check with 'arecord -l'
  wake_word_sensitivity: 0.7     # Adjust for your environment

safety:
  max_boost_pressure: 15.0       # Set safe limit for your engine
  engine_temp_critical: 105.0    # Adjust for your cooling system
```

### 3.2 Permissions Setup

#### Add User to Groups
```bash
sudo usermod -a -G dialout,spi,i2c,gpio,audio pi
```

#### Set File Permissions
```bash
sudo chown -R pi:pi /opt/automotive-llm
chmod +x src/main.py
```

#### Create Log Directory
```bash
sudo mkdir -p /var/log/automotive-llm
sudo chown pi:pi /var/log/automotive-llm
```

### 3.3 Systemd Service Setup

#### Create Service File
```bash
sudo nano /etc/systemd/system/automotive-llm.service
```

Add:
```ini
[Unit]
Description=Automotive LLM System
After=network.target ollama.service can-setup.service
Wants=network.target
Requires=ollama.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/automotive-llm
Environment=PATH=/opt/automotive-llm/venv/bin
ExecStart=/opt/automotive-llm/venv/bin/python src/main.py --config config.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable automotive-llm.service
```

## Step 4: Testing and Validation

### 4.1 Component Testing

#### Test OBD-II Connection
```bash
python3 -c "
import obd
conn = obd.OBD('/dev/ttyUSB0')
print(f'OBD Status: {conn.status()}')
if conn.status() == obd.OBDStatus.CAR_CONNECTED:
    rpm = conn.query(obd.commands.RPM)
    print(f'Engine RPM: {rpm.value}')
conn.close()
"
```

#### Test CAN Interface
```bash
# Send test CAN message
cansend can0 123#DEADBEEF

# Monitor CAN traffic
candump can0
```

#### Test Audio System
```bash
# Test microphone
python3 -c "
import pyaudio
import numpy as np

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)
print('Listening for 5 seconds...')
data = stream.read(5 * 16000)
print(f'Captured {len(data)} bytes of audio')
stream.close()
p.terminate()
"
```

#### Test Ollama
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b-instruct-q4_K_M",
  "prompt": "What is the ideal operating temperature for a car engine?",
  "stream": false
}'
```

### 4.2 System Integration Test

#### Start System in Debug Mode
```bash
cd /opt/automotive-llm
source venv/bin/activate
python src/main.py --debug
```

#### Expected Output
```
🚗 Initializing Automotive LLM System...
✅ OBD-II interface ready
✅ CAN bus interface ready
✅ Vehicle Manager initialized
🧠 Initializing LLM Controller...
✅ LLM ready with model: llama3.1:8b-instruct-q4_K_M
🌡️ Initializing HVAC Controller...
✅ HVAC Controller initialized
🛡️ Initializing Safety Monitor...
✅ Safety Monitor initialized with X rules
🎤 Initializing Voice Manager...
✅ Voice Manager initialized successfully
✅ System Controller initialized successfully
🎯 Starting Automotive LLM System...
🎤 Started listening for wake words...
✅ System started successfully
🎤 Automotive LLM System started - Listening for commands...
```

### 4.3 Voice Command Testing

#### Test Wake Words
1. Say "Hey Car" and wait for response
2. Try "Vehicle Assistant" for secondary wake word
3. Test "Emergency Override" for emergency mode

#### Test Basic Commands
```
"Hey Car, what's my engine temperature?"
"Turn on the air conditioning"
"Set temperature to 72 degrees"
"Turn up the volume"
"Dim the lights to 50 percent"
```

## Step 5: Production Deployment

### 5.1 Service Management

#### Start Service
```bash
sudo systemctl start automotive-llm.service
```

#### Check Status
```bash
sudo systemctl status automotive-llm.service
```

#### View Logs
```bash
journalctl -u automotive-llm.service -f
```

### 5.2 Monitoring Setup

#### Log Rotation
```bash
sudo nano /etc/logrotate.d/automotive-llm
```

Add:
```
/var/log/automotive-llm/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload automotive-llm.service
    endscript
}
```

#### Health Check Script
```bash
nano /opt/automotive-llm/scripts/health-check.sh
```

Add:
```bash
#!/bin/bash
# Basic health check script

# Check if service is running
if ! systemctl is-active --quiet automotive-llm.service; then
    echo "Service not running, restarting..."
    sudo systemctl restart automotive-llm.service
fi

# Check disk space
if [ $(df /opt/automotive-llm | tail -1 | awk '{print $5}' | sed 's/%//') -gt 90 ]; then
    echo "Disk space warning: >90% full"
fi

# Check temperature
temp=$(vcgencmd measure_temp | sed 's/temp=//' | sed 's/°C//')
if (( $(echo "$temp > 70" | bc -l) )); then
    echo "Temperature warning: ${temp}°C"
fi
```

Make executable and add to crontab:
```bash
chmod +x /opt/automotive-llm/scripts/health-check.sh
crontab -e
# Add: */5 * * * * /opt/automotive-llm/scripts/health-check.sh
```

## Troubleshooting

### Common Issues

#### 1. OBD-II Not Connecting
- Check USB cable and adapter
- Verify vehicle is running or in accessory mode
- Try different baud rates: 9600, 38400, 115200
- Check adapter compatibility with vehicle

#### 2. CAN Bus Not Working
- Verify SPI is enabled in raspi-config
- Check wiring connections
- Confirm CAN termination resistors (120Ω each end)
- Use oscilloscope to verify signal integrity

#### 3. Audio Issues
- Check USB microphone connection
- Verify audio device index with `arecord -l`
- Test with different sample rates
- Check for audio conflicts with other processes

#### 4. Ollama Not Responding
- Check service status: `systemctl status ollama`
- Verify model is downloaded: `ollama list`
- Check available memory: `free -h`
- Try smaller model if memory constrained

#### 5. Permission Errors
- Ensure user is in correct groups
- Check file ownership: `ls -la /opt/automotive-llm`
- Verify device permissions: `ls -la /dev/ttyUSB*`

### Debug Commands

#### View Real-time Logs
```bash
tail -f /var/log/automotive-llm/system.log
journalctl -u automotive-llm.service -f
```

#### Check System Resources
```bash
htop
iotop
lsof | grep automotive-llm
```

#### Network Diagnostics
```bash
ss -tulpn | grep 11434  # Ollama
ping localhost
curl -I http://localhost:11434
```

## Safety Considerations

### Installation Safety
- Always work with vehicle power disconnected
- Use proper ESD protection when handling electronics
- Verify all connections before applying power
- Test thoroughly before driving

### Operational Safety
- Never override critical safety systems
- Maintain manual control capabilities
- Regular backup of configuration
- Monitor system health continuously

### Legal Compliance
- Check local regulations for vehicle modifications
- Ensure modifications don't void warranty
- Document all changes for insurance purposes
- Follow automotive electrical standards

## Next Steps

After successful installation:

1. **Read the [User Guide](user-guide.md)** for voice commands
2. **Review [Developer Guide](developer-guide.md)** for customization
3. **Configure vehicle-specific settings** in config.yaml
4. **Train voice recognition** with your voice patterns
5. **Set up monitoring and alerting** for production use

For ongoing maintenance and updates, see the [Maintenance Guide](maintenance.md).