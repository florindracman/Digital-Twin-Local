# Unit Tests for MQTT Vehicle Digital Twin Application

## Overview
This directory contains comprehensive unit tests for all components of the MQTT Vehicle Digital Twin application.

## Test Structure
- `test_plugin_manager.py` - Tests for plugin loading and management
- `test_listener_base.py` - Tests for base plugin class
- `test_vehicle_digital_twin_db.py` - Tests for database operations
- `test_rpc_server_plugin.py` - Tests for RPC server plugin
- `test_trigger_listener_plugin.py` - Tests for trigger listener plugin
- `test_vehicle_digital_twin.py` - Tests for vehicle digital twin logic
- `test_integration.py` - Integration tests

## Running Tests

### Run all tests:
```bash
cd tests
python -m unittest discover -v