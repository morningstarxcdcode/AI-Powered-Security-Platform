"""
Scout Configuration Management
Handles configuration loading from multiple sources with environment variable override support.
"""
import json
import os
from typing import Any, Dict, Optional

import yaml

from scout.logging import log_error

# Configuration file names
CONFIG_YAML = 'scout.yaml'
CONFIG_YML = 'scout.yml'
CONFIG_JSON = 'scout.json'
CONFIG_HIDDEN_YAML = '.scout.yaml'


class ScoutConfig:
    """Advanced configuration management for Scout CLI."""

    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._load_default_config()

        # Load from file if specified or found
        if config_path and os.path.exists(config_path):
            self.load(config_path)
        elif os.path.exists(CONFIG_YAML):
            self.load(CONFIG_YAML)
        elif os.path.exists(CONFIG_YML):
            self.load(CONFIG_YML)
        elif os.path.exists(CONFIG_JSON):
            self.load(CONFIG_JSON)
        elif os.path.exists(CONFIG_HIDDEN_YAML):
            self.load(CONFIG_HIDDEN_YAML)

    def _load_default_config(self):
        """
Load default configuration values."""
        self._config = {
            'scan': {
                'timeout': 10,
                'user_agent': 'Scout/1.0',
                'retries': 2,
                'follow_redirects': True,
                'max_concurrent_scans': 5
            },
            'reporting': {
                'default_format': 'json',
                'include_charts': True,
                'include_metadata': True
            },
            'notifications': {
                'enabled': False,
                'email': False,
                'slack': False,
                'sms': False,
                'telegram': False
            },
            'security': {
                'encrypt_secrets': True,
                'audit_logging': True,
                'require_auth': False
            },
            'api': {
                'rate_limit': True,
                'cache_results': True,
                'cache_ttl': 3600
            }
        }

    def load(self, path: str):
        """
Load configuration from a file."""
        try:
            with open(path, 'r') as f:
                if path.endswith(('.yaml', '.yml')):
                    file_config = yaml.safe_load(f) or {}
                elif path.endswith('.json'):
                    file_config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {path}")

            # Deep merge with existing config
            self._deep_merge(self._config, file_config)

        except Exception as e:
            log_error(f"Failed to load config from {path}: {e}")

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with environment variable override.
        Supports dot notation (e.g., 'scan.timeout').
        """
        # Check environment variable first (convert dots to underscores and uppercase)
        env_key = f"SCOUT_{key.replace('.', '_').upper()}"
        env_value = os.getenv(env_key)

        if env_value is not None:
            # Try to convert to appropriate type
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            try:
                # Try int first, then float
                if '.' not in env_value:
                    return int(env_value)
                else:
                    return float(env_value)
            except ValueError:
                return env_value

        # Get from config file
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: str = CONFIG_YAML):
        """
Save current configuration to file."""
        try:
            with open(path, 'w') as f:
                if path.endswith(('.yaml', '.yml')):
                    yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
                elif path.endswith('.json'):
                    json.dump(self._config, f, indent=2)
                else:
                    raise ValueError(f"Unsupported config file format: {path}")
        except Exception as e:
            print(f"Error saving config to {path}: {e}")

    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self._config.copy()

    def validate(self) -> bool:
        """
Validate the current configuration."""
        required_sections = ['scan', 'reporting', 'notifications', 'security']

        for section in required_sections:
            if section not in self._config:
                print(f"Missing required config section: {section}")
                return False

        # Validate specific values
        scan_timeout = self.get('scan.timeout')
        if not isinstance(scan_timeout, int) or scan_timeout <= 0:
            print("Invalid scan.timeout: must be a positive integer")
            return False

        return True

# Global config instance
config = ScoutConfig()

def load_legacy_config(config_path=None):
    """Legacy compatibility function."""
    return ScoutConfig(config_path)
