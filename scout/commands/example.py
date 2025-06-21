"""
Scout example command module.
"""

import click
from scout.logging import log_info, log_error


@click.command()
@click.pass_context
def example(ctx):
    """
    Example command for Scout CLI.
    """
    log_info(f"Executing example command")
    click.echo(f"{cmd_name} command executed successfully")


def register(cli):
    """Register this command with the CLI."""
    cli.add_command(example)
