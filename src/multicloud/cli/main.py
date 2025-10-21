"""
MultiCloud CLI main entry point.
"""

import tomllib
from pathlib import Path
import click

# Import Command modules
from .commands import config_command


def get_version() -> str:
    """
    Get the package version from pyproject.toml.
    """
    try:
        # Find pyproject.toml relative to this file
        project_root = Path(__file__).parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        return pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "unknown"


@click.group()
@click.version_option(version=get_version(), prog_name="MultiCloud CLI")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    MultiCloud Framework CLI Tools

    A command-line interface for creating multi-cloud serverless functions.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


# Add commands to the CLI group
cli.add_command(config_command.config)
