"""
Test configuration for pytest
"""
import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    config = {
        'api_keys': {
            'openai': 'test-key',
            'anthropic': 'test-key'
        },
        'thresholds': {
            'critical': 9.0,
            'high': 7.0,
            'medium': 4.0,
            'low': 1.0
        },
        'output': {
            'format': 'json',
            'file': None,
            'directory': 'scout_reports'
        }
    }
    return config


@pytest.fixture
def mock_web3():
    """Mock Web3 for blockchain tests."""
    with patch('scout.blockchain_security.Web3') as mock_web3:
        mock_web3.return_value.is_connected.return_value = True
        mock_web3.return_value.eth.block_number = 18000000
        yield mock_web3


@pytest.fixture
def mock_voice_deps():
    """Mock voice dependencies for testing."""
    with patch('scout.voice_assistant.sr') as mock_sr, \
         patch('scout.voice_assistant.pyttsx3') as mock_pyttsx3:
        mock_sr.Recognizer.return_value = None
        mock_sr.Microphone.return_value = None
        mock_pyttsx3.init.return_value = None
        yield mock_sr, mock_pyttsx3
