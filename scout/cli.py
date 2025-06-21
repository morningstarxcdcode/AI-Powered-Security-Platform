import importlib
import os
import pkgutil

import click

from scout.logging import log_error, log_info
from scout.voice_assistant import speak_if_available, start_voice_mode


@click.group()
@click.option(
    '--voice', '-v',
    is_flag=True,
    help='Enable voice narration for all commands'
)
@click.pass_context
def cli(ctx, voice):
    """Scout: Advanced Security Reconnaissance CLI Tool with Voice Assistant"""
    # Store voice flag in context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj['voice_enabled'] = voice

    log_info(f"Scout CLI initialized with voice_enabled={voice}")
    
    if voice:
        speak_if_available(
            "Scout CLI initialized with voice assistance activated."
        )


@cli.command()
def voice(ctx):
    """Start interactive voice command mode"""
    log_info("Starting voice command mode")
    speak_if_available("Starting Scout CLI interactive voice assistant.")
    start_voice_mode()


# Dynamically load commands from scout/commands
commands_path = os.path.join(os.path.dirname(__file__), 'commands')
for loader, module_name, is_pkg in pkgutil.iter_modules([commands_path]):
    try:
        module = importlib.import_module(f'scout.commands.{module_name}')
        if hasattr(module, 'register'):
            module.register(cli)
            log_info(f"Loaded command module: {module_name}")
    except Exception as e:
        log_error(f"Failed to load command module {module_name}: {e}")
