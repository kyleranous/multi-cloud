"""
MultiCloud Configuration Manager CLI Commands
"""

# import os
from pathlib import Path
from typing import Dict, Any  # , Optional
import yaml
import click


class ConfigManager:
    """
    A class to set and manage MultiCloud configuration settings.
    """

    def __init__(self):
        self.config_dir = self._find_project_root() / ".multicloud"
        self.config_file = self.config_dir / "config.yaml"
        self._config_data = None

    def _find_project_root(self) -> Path:
        """
        Find the project root directory
        by looking for a .multicloud directory or defaulting to home directory.
        """
        return Path.cwd()

    def ensure_config_dir(self):
        """
        Ensure the configuration directory exists.
        """
        self.config_dir.mkdir(exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the YAML file.
        """
        if self._config_data is not None:
            return self._config_data

        if not self.config_file.exists():
            self._config_data = self._create_default_config()
            self.save_config()
        else:
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self._config_data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                click.echo(f"Error loading config: {e}")
                self._config_data = self._create_default_config()

        return self._config_data

    def save_config(self):
        """
        Save the current configuration to the YAML file.
        """
        # Ensure the directory exists before trying to write the config
        self.ensure_config_dir()

        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config_data, f, default_flow_style=False, indent=2)

    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default coniguration
        """
        return {
            "author": {"name": "", "email": ""},
            "defaults": {
                "runtime": "python",
                "memory": "128Mi",
                "timeout": "30s",
                "log_level": "INFO",
                "license": "",
                "version": "0.1.0",
            },
            "platforms": {"knative": {}, "aws": {}, "azure": {}, "gcp": {}},
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        """
        config = self.load_config()

        keys = key.split(".")
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """
        Set a configuration value using dot notation.
        """
        config = self.load_config()

        keys = key.split(".")
        current = config

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value
        self._config_data = config
        self.save_config()

    def get_template_context(self) -> Dict[str, Any]:
        """
        Get context variables for template rendering
        """
        config = self.load_config()

        return {
            "author_name": config.get("author", {}).get("name", ""),
            "author_email": config.get("author", {}).get("email", ""),
            "default_runtime": config.get("defaults", {}).get("runtime", "python"),
            "default_platform": config.get("defaults", {}).get("platform", "knative"),
            "default_memory": config.get("defaults", {}).get("memory", "128Mi"),
            "default_timeout": config.get("defaults", {}).get("timeout", "30s"),
            "default_log_level": config.get("defaults", {}).get("log_level", "INFO"),
            "default_license": config.get("defaults", {}).get("license", "MIT"),
            "default_version": config.get("defaults", {}).get("version", "0.1.0"),
        }


# Global instance
config_manager = ConfigManager()
