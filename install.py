#!/usr/bin/env python3
"""
Scout CLI Installation Script
Allows users to install different feature sets based on their needs.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Constants
CORE_REQUIREMENTS = "requirements-core.txt"
AI_REQUIREMENTS = "requirements-ai.txt"
BLOCKCHAIN_REQUIREMENTS = "requirements-blockchain.txt"
WEB_REQUIREMENTS = "requirements-web.txt"
VOICE_REQUIREMENTS = "requirements-voice.txt"
FULL_REQUIREMENTS = "requirements-full.txt"


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def install_requirements(req_file):
    """Install requirements from a specific file."""
    if not Path(req_file).exists():
        print(f"❌ Requirements file {req_file} not found")
        return False

    return run_command(f"pip install -r {req_file}", f"Installing {req_file}")


def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description="Scout CLI Installation Script")
    parser.add_argument(
        "--profile",
        choices=["core", "ai", "blockchain", "web", "voice", "full", "dev"],
        default="core",
        help="Installation profile (default: core)"
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade existing packages"
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="Install for current user only"
    )

    args = parser.parse_args()

    print("🚀 Scout CLI Installation")
    print(f"Profile: {args.profile}")
    print("-" * 40)

    # Build pip command options
    pip_options = []
    if args.upgrade:
        pip_options.append("--upgrade")
    if args.user:
        pip_options.append("--user")

    # Update pip command template
    global pip_command_template
    pip_command_template = f"pip install {' '.join(pip_options)} -r"

    # Install based on profile
    success = True

    if args.profile == "core":
        print("📦 Installing core dependencies...")
        success &= install_requirements(CORE_REQUIREMENTS)

    elif args.profile == "ai":
        print("📦 Installing core + AI dependencies...")
        success &= install_requirements(CORE_REQUIREMENTS)
        success &= install_requirements(AI_REQUIREMENTS)

    elif args.profile == "blockchain":
        print("📦 Installing core + blockchain dependencies...")
        success &= install_requirements(CORE_REQUIREMENTS)
        success &= install_requirements(BLOCKCHAIN_REQUIREMENTS)

    elif args.profile == "web":
        print("📦 Installing core + web dashboard dependencies...")
        success &= install_requirements(CORE_REQUIREMENTS)
        success &= install_requirements(WEB_REQUIREMENTS)

    elif args.profile == "voice":
        print("📦 Installing core + voice assistant dependencies...")
        success &= install_requirements(CORE_REQUIREMENTS)
        success &= install_requirements(VOICE_REQUIREMENTS)

    elif args.profile == "full":
        print("📦 Installing all dependencies...")
        success &= install_requirements(FULL_REQUIREMENTS)

    elif args.profile == "dev":
        print("📦 Installing development dependencies...")
        success &= install_requirements(FULL_REQUIREMENTS)
        # Additional dev tools
        dev_packages = [
            "pre - commit >= 3.6.0",
            "tox >= 4.11.0",
            "sphinx >= 7.2.0",
            "sphinx - rtd - theme >= 1.3.0"
        ]
        for package in dev_packages:
            run_command(f"pip install {' '.join(pip_options)} {package}", f"Installing {package}")

    # Install Scout CLI in development mode
    print("📦 Installing Scout CLI...")
    if args.user:
        success &= run_command("pip install --user -e .", "Installing Scout CLI (editable)")
    else:
        success &= run_command("pip install -e .", "Installing Scout CLI (editable)")

    print("-" * 40)
    if success:
        print("🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Run 'scout --help' to see available commands")
        print("2. Copy scout.yaml.example to scout.yaml and configure")
        print("3. Check out the documentation and examples")

        # Profile - specific next steps
        if args.profile in ["ai", "full", "dev"]:
            print("4. Configure AI provider API keys in environment variables")
        if args.profile in ["blockchain", "full", "dev"]:
            print("4. Configure Web3 provider endpoints for blockchain analysis")
        if args.profile in ["web", "full", "dev"]:
            print("4. Configure Redis connection for real - time monitoring")

    else:
        print("❌ Installation completed with errors")
        print("Please check the error messages above and try again")
        sys.exit(1)


def update_pip_command():
    """Update the global pip command template for install_requirements function."""
    global run_command
    original_run_command = run_command

    def custom_run_command(command, description):
        # Replace the pip install part with our custom options
        if command.startswith("pip install -r"):
            req_file = command.split()[-1]
            command = f"{pip_command_template} {req_file}"
        return original_run_command(command, description)

    run_command = custom_run_command

    

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
