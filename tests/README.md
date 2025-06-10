# Testing Scripts

This directory contains all testing and development scripts for the Automotive LLM System.

## Test Scripts

### Core System Tests
- **test_system.py** - Basic system functionality test
- **comprehensive_test.py** - Complete system test with data generation and export

### Dashboard Tests
- **enhanced_dashboard.py** - Enhanced dashboard with system checks and live monitoring
- **test_dashboard.py** - Dashboard functionality tests
- **test_dashboard_data.py** - Dashboard data flow tests

### Virtual Drive Tests
- **virtual_drive_test.py** - Virtual drive simulation
- **bridge_virtual_drive.py** - Bridge virtual drive data to dashboard
- **direct_dashboard_update.py** - Direct JavaScript injection for live data demonstration
- **inject_live_data.py** - Live data injection via API

### Test Suite
- **run_test_suite.py** - Runs all tests in sequence

## Usage

### Quick System Test
```bash
python3 tests/test_system.py
```

### Complete System Test with Exports
```bash
python3 tests/comprehensive_test.py
```

### Enhanced Dashboard with Live Monitoring
```bash
python3 tests/enhanced_dashboard.py
```

### Virtual Drive Simulation
```bash
python3 tests/virtual_drive_test.py
```

### Run All Tests
```bash
python3 tests/run_test_suite.py
```

## Notes

- All tests run in mock mode by default
- Enhanced dashboard provides real-time system monitoring
- Virtual drive tests generate realistic automotive data
- Export tests verify data logging and export functionality
- JavaScript injection script bypasses backend data collection issues

## Requirements

Tests require the main system dependencies. Install with:
```bash
pip install -r requirements.txt
```