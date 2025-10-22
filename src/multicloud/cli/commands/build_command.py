"""
MultiCloud CLI main entry point for build commands
"""

import click
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import shutil

# pylint: disable=relative-beyond-top-level
from ..config.config_manager import config_manager


class BuildError(Exception):
    """
    Exception raised for errors during the build process.
    """


class MultiCloudBoulder:
    """
    Handles building platform-specific deployment packages.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.config_file = project_path / "multicloud.yaml"
        self.build_dir = project_path / "build"
        self.config = None

    def load_config(self) -> Dict[str, Any]:
        """
        Load the multicloud.yaml configuration file.
        """
        # Check for multicloud.yaml in the project path
        if not self.config_file.exists():
            raise BuildError(f"multicloud.yaml not found in {self.project_path}")

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            return self.config
        except yaml.YAMLError as e:
            raise BuildError(f"Invalid multicloud.yaml: {e}") from e
