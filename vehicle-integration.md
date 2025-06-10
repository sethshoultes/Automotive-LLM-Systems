# Vehicle Integration Protocols

## OBD-II (On-Board Diagnostics) Integration

### OBD-II Basics
**Standard Connector**: 16-pin DLC (Data Link Connector)
- Located under dashboard, driver's side
- Standardized since 1996 (US vehicles)
- Universal diagnostic access point
- 12V power available on pins 4, 16

### OBD-II Protocols
**ISO 9141-2** (K-Line)
- Single wire communication
- 10.4 kbaud data rate
- Common in Asian vehicles (pre-2008)

**ISO 14230-4** (KWP2000)
- Keyword Protocol 2000
- Enhanced version of K-Line
- Variable baud rates

**ISO 15765-4** (CAN)
- Controller Area Network
- 500 kbaud or 250 kbaud
- Most modern vehicles (2008+)
- High-speed, reliable communication

**SAE J1850**
- Variable Pulse Width (VPW) - 41.6 kbaud
- Pulse Width Modulation (PWM) - 10.4 kbaud
- Primarily US domestic vehicles

### Accessible OBD-II Data
**Engine Parameters**
- RPM, coolant temperature, intake air temp
- Mass air flow, throttle position
- Fuel system status, fuel trim values
- Ignition timing advance

**Emissions Data**
- Oxygen sensor readings
- Catalytic converter efficiency
- Evaporative emission control
- EGR system status

**Vehicle Speed & Load**
- Vehicle speed sensor
- Calculated engine load
- Absolute throttle position
- Commanded throttle actuator

**Diagnostic Information**
- Diagnostic trouble codes (DTCs)
- Freeze frame data
- Readiness monitors status
- MIL (Check Engine Light) status

### OBD-II Limitations
- Read-only access (no control commands)
- Limited to emissions-related systems
- Standardized parameters only
- No access to comfort/convenience systems

## CAN Bus Integration

### CAN Bus Architecture
**Physical Layer**
- Twisted pair wires (CAN-H, CAN-L)
- Differential signaling (2.5V ±2V)
- 120Ω termination resistors
- Bus topology with multiple nodes

**Data Rates**
- High-speed CAN: 500 kbps (powertrain)
- Medium-speed CAN: 125 kbps (body systems)
- Low-speed CAN: 33.3 kbps (comfort systems)

### CAN Message Format
**Standard Frame (11-bit ID)**
```
| SOF | ID(11) | RTR | IDE | r0 | DLC(4) | DATA(0-64) | CRC(15) | ACK | EOF |
```

**Extended Frame (29-bit ID)**
```
| SOF | ID(11) | SRR | IDE | ID(18) | RTR | r1 | r0 | DLC(4) | DATA(0-64) | CRC(15) | ACK | EOF |
```

### Vehicle CAN Networks
**Powertrain CAN**
- Engine control module (ECM)
- Transmission control module (TCM)
- High-speed network (500 kbps)
- Critical safety systems

**Body CAN**
- Body control module (BCM)
- Lighting, doors, windows
- Medium-speed network (125 kbps)
- Comfort and convenience

**Infotainment CAN**
- Audio system, navigation
- Climate control interface
- Various speed networks
- User interface systems

### CAN Message Examples
**Engine RPM** (typical)
- ID: 0x201
- Data: [RPM_HIGH, RPM_LOW, ...]
- Formula: RPM = (RPM_HIGH * 256 + RPM_LOW) / 4

**Vehicle Speed**
- ID: 0x3E9
- Data: [SPEED_HIGH, SPEED_LOW, ...]
- Formula: Speed = (SPEED_HIGH * 256 + SPEED_LOW) * 0.01 km/h

**HVAC Temperature**
- ID: 0x3F1
- Data: [TEMP_SETPOINT, FAN_SPEED, MODE, ...]

## Hardware Integration

### ELM327 OBD-II Adapter
**Advantages**
- Plug-and-play OBD-II access
- Multiple protocol support
- AT command interface
- Wide compatibility

**Limitations**
- Limited to OBD-II standard PIDs
- No direct CAN bus access
- Slower response times
- No transmission of custom messages

### MCP2515 CAN Controller
**Features**
- SPI interface to Raspberry Pi
- Hardware message filtering
- Multiple receive buffers
- Interrupt-driven operation

**Wiring to Raspberry Pi**
```
MCP2515    Raspberry Pi 5
VCC    ->  3.3V (Pin 1)
GND    ->  GND (Pin 6)
CS     ->  GPIO 8 (Pin 24)
SO     ->  GPIO 9 (Pin 21)
SI     ->  GPIO 10 (Pin 19)
SCK    ->  GPIO 11 (Pin 23)
INT    ->  GPIO 25 (Pin 22)
```

### CAN Transceiver Integration
**MCP2562 CAN Transceiver**
- Converts between CAN controller and bus
- 3.3V logic level compatible
- Fault protection features
- Slope control for EMI reduction

## Vehicle-Specific Protocols

### Ford (FoMoCo)
**MS-CAN** (Medium Speed CAN)
- 125 kbps network
- Body and convenience systems
- Climate control, lighting

**HS-CAN** (High Speed CAN)
- 500 kbps network
- Powertrain systems
- ABS, airbag systems

### General Motors
**GMLAN** (GM Local Area Network)
- Based on ISO 15765-4
- Single and dual-wire CAN
- Class 2 (10.4 kbps) legacy support

### Chrysler/Stellantis
**CCD** (Chrysler Collision Detection)
- Legacy 2-wire bus
- 7.8 kbps data rate
- Body control modules

**PCI** (Programmable Communication Interface)
- High-speed network
- ISO 9141 based
- Engine and transmission

### European Vehicles
**K-Line/L-Line**
- ISO 9141-2 / ISO 14230
- Single-wire communication
- Diagnostic access

**FlexRay**
- High-speed deterministic network
- X-by-wire applications
- Safety-critical systems

## Integration Safety Considerations

### Electrical Safety
**Isolation Requirements**
- Optical isolation for CAN interfaces
- Separate power domains
- Overcurrent protection
- Reverse polarity protection

**Ground Loops**
- Common ground reference
- Twisted pair cable shielding
- Proper connector grounding

### Network Safety
**Message Validation**
- CRC checking
- Sequence number validation
- Timeout detection
- Duplicate message filtering

**Bus Monitoring**
- Error frame detection
- Bus-off condition handling
- Automatic recovery procedures
- Network health monitoring

### Control System Safety
**Command Verification**
- Two-stage command confirmation
- Safety parameter validation
- Emergency stop capability
- Fail-safe default states

**Access Control**
- Read-only mode by default
- Explicit write permission
- Safety-critical system lockout
- Administrative override

## Implementation Strategy

### Phase 1: OBD-II Integration
1. ELM327 adapter connection
2. Basic diagnostic data reading
3. Real-time parameter monitoring
4. Fault code interpretation

### Phase 2: CAN Bus Access
1. MCP2515 controller installation
2. Vehicle-specific protocol research
3. Message sniffing and analysis
4. Protocol reverse engineering

### Phase 3: Control Implementation
1. Safe command transmission
2. Response validation
3. Emergency safety protocols
4. Comprehensive testing

### Development Tools
**Hardware**
- CAN bus analyzer (CANoe, Kvaser)
- Oscilloscope for signal analysis
- Protocol-specific scan tools

**Software**
- Wireshark with CAN plugins
- Python-CAN library
- Vehicle-specific databases (DBC files)
- Reverse engineering tools

## Legal and Warranty Considerations

### Warranty Impact
- OBD-II access generally warranty-safe
- CAN bus modifications may void warranty
- Document all changes for warranty claims
- Consider removable installations

### Regulatory Compliance
- FCC Part 15 for electronic devices
- SAE J1962 OBD-II connector standards
- ISO 11898 CAN bus standards
- Vehicle-specific regulations

### Safety Standards
- ISO 26262 functional safety
- IEC 61508 safety integrity levels
- Automotive SPICE development process
- MISRA C coding standards