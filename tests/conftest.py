import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock

@pytest.fixture
def temp_state_file(tmp_path):
    """Creates a temporary state file for testing."""
    state_file = tmp_path / ".sn_state.json"
    # Patch the STATE_FILE in the state module
    import sn.state as state_module
    original_state_file = state_module.STATE_FILE
    state_module.STATE_FILE = state_file
    
    yield state_file
    
    # Teardown: Restore original
    state_module.STATE_FILE = original_state_file

@pytest.fixture
def mock_adb_client(mocker):
    """Mocks the adbutils client."""
    mock_client = MagicMock()
    mock_device = MagicMock()
    mock_client.device_list.return_value = [mock_device]
    # Default serial looking like IP for wireless preference test
    mock_device.serial = "192.168.1.5:5555" 
    
    patcher = mocker.patch("adbutils.AdbClient", return_value=mock_client)
    yield mock_client
    
@pytest.fixture
def mock_device_instance(mock_adb_client):
    return mock_adb_client.device_list.return_value[0]
