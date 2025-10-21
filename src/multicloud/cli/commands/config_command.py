"""
Configuration Management Commands
"""

import click
import yaml

from ..config.config_manager import (
    config_manager,
)  # pylint: disable=relative-beyond-top-level


@click.group()
def config():
    """
    Manage MultiCloud CLI configuration
    """


@config.command()
@click.argument("key", required=False)
def get(key: str):
    """
    Get configuration value(s)

    Examples:
        multicloud config get author.name
        multicloud config get defaults.runtime
        multicloud config get # Show all config
    """
    if key:
        value = config_manager.get(key)
        if value is not None:
            click.echo(f"{key}: {value}")
        else:
            click.echo(f"Configuration key '{key}' not found.")
    else:
        full_config = config_manager.load_config()
        click.echo(yaml.dump(full_config, default_flow_style=False, indent=2))


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):  # pylint: disable=redefined-builtin
    """
    Set configuration value

    Examples:
        multicloud config set author.name "New Author"
        multicloud config set defaults.runtime "python3.11"
    """
    try:
        config_manager.set(key, value)
        click.echo(f"Set '{key}' to '{value}' in configuration.")
    except Exception as e:  # pylint: disable=broad-except
        click.echo(f"Error setting configuration '{key}': {e}")


@config.command()
def init():
    """Initialize configuration with guided setup"""
    click.echo("🚀 MultiCloud CLI Configuration Setup")
    click.echo("")

    # Debug: Show where config will be saved
    click.echo(f"Config will be saved to: {config_manager.config_file}")
    click.echo(f"Config directory: {config_manager.config_dir}")
    click.echo("")

    # Author information
    click.echo("📝 Author Information")
    name = click.prompt("Your name", default="")
    email = click.prompt("Your email", default="")

    # Default settings
    click.echo("\n⚙️  Default Settings")
    runtime = click.prompt(
        "Default runtime", type=click.Choice(["python", "node", "go"]), default="python"
    )

    memory = click.prompt("Default memory", default="128Mi")
    timeout = click.prompt("Default timeout", default="30s")

    # Save all settings
    config_manager.set("author.name", name)
    config_manager.set("author.email", email)
    config_manager.set("defaults.runtime", runtime)
    config_manager.set("defaults.memory", memory)
    config_manager.set("defaults.timeout", timeout)

    click.echo("Configuration saved!")
    click.echo(f"Config file: {config_manager.config_file}")


@config.command()
def path():
    """Show configuration file path"""
    click.echo(f"Config file: {config_manager.config_file}")
    click.echo(f"Config directory: {config_manager.config_dir}")


@config.command()
def reset():
    """Reset configuration to defaults"""
    if click.confirm("Are you sure you want to reset all configuration?"):
        config_manager.config_file.unlink(missing_ok=True)
        config_manager._config_data = None  # pylint: disable=protected-access
        click.echo("Configuration reset to defaults")
