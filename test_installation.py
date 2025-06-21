#!/usr/bin/env python3
"""
Scout CLI - Comprehensive Test & Validation Script
Validates installation, configuration, and core functionality.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_test_result(name, status, details=""):
    """Print test result."""
    status_emoji = "✅" if status else "❌"
    print(f"{status_emoji} {name:<40} {details}")

    """Test Python version compatibility."""
    import sys
    version = sys.version_info
    compatible = version >= (3, 8)
    print_test(
        "Python Version",
        compatible,
        f"v{version.major}.{version.minor}.{version.micro}"
    )
    return compatible

    """Test core module imports."""
    tests = []

    try:
        import scout
        tests.append(("Scout package", True))
    except ImportError as e:
        tests.append(("Scout package", False, str(e)))

    try:
        import scout.cli
        tests.append(("CLI module", True))
    except ImportError as e:
        tests.append(("CLI module", False, str(e)))

    try:
        import scout.config
        tests.append(("Config module", True))
    except ImportError as e:
        tests.append(("Config module", False, str(e)))

    for test_name, status, *details in tests:
        print_test(test_name, status, details[0] if details else "")

    return all(test[1] for test in tests)

    """Test advanced module imports."""
    tests = []

    # AI Engine
    try:
        import scout.ai_engine
        tests.append(("AI Engine", True))
    except ImportError as e:
        tests.append(("AI Engine", False, str(e)))

    # Real - time Monitor
    try:
        import scout.realtime_monitor
        tests.append(("Real - time Monitor", True))
    except ImportError as e:
        tests.append(("Real - time Monitor", False, str(e)))

    # Blockchain Security
    try:
        import scout.blockchain_security
        tests.append(("Blockchain Security", True))
    except ImportError as e:
        tests.append(("Blockchain Security", False, str(e)))

    for test_name, status, *details in tests:
        print_test(test_name, status, details[0] if details else "")

    return all(test[1] for test in tests)

    """Test CLI command accessibility."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "scout.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        success = result.returncode == 0 and "Scout CLI" in result.stdout
        print_test("CLI Help Command", success)
        return success
    except Exception as e:
        print_test("CLI Help Command", False, str(e))
        return False

    """Test configuration file existence and validity."""
    config_file = Path("scout.yaml")
    exists = config_file.exists()
    print_test("Config File Exists", exists, str(config_file))

    if exists:
        try:
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
            valid = isinstance(config, dict)
            print_test("Config File Valid", valid)
            return valid
        except Exception as e:
            print_test("Config File Valid", False, str(e))
            return False

    return exists

    """Test key dependencies."""
    dependencies = [
        ("click", "CLI framework"),
        ("requests", "HTTP client"),
        ("yaml", "YAML parser"),
        ("jinja2", "Template engine"),
        ("cryptography", "Cryptographic operations")
    ]

    all_good = True
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print_test(f"{desc}", True, f"({dep})")
        except ImportError:
            print_test(f"{desc}", False, f"({dep} missing)")
            all_good = False

    return all_good

    """Test advanced dependencies (optional)."""
    advanced_deps = [
        ("openai", "OpenAI API"),
        ("anthropic", "Anthropic API"),
        ("fastapi", "FastAPI framework"),
        ("redis", "Redis client"),
        ("web3", "Web3 library")
    ]

    available = []
    for dep, desc in advanced_deps:
        try:
            __import__(dep)
            print_test(f"{desc}", True, f"({dep})")
            available.append(dep)
        except ImportError:
            print_test(f"{desc}", False, f"({dep} not installed)")

    return available

    """Test project file structure."""
    required_files = [
        "scout / __init__.py",
        "scout / cli.py",
        "scout / config.py",
        "requirements.txt",
        "README.md"
    ]

    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_test(f"File: {file_path}", exists)
        if not exists:
            all_exist = False

    return all_exist

async def test_async_functionality():
    """Test async functionality."""
    try:
        # Simple async test
        async def sample_async():
            await asyncio.sleep(0.01)
            return True

        result = await sample_async()
        print_test("Async Support", result)
        return result
    except Exception as e:
        print_test("Async Support", False, str(e))
        return False

    """Generate a summary report."""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["status"])
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print_header("TEST SUMMARY")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 Scout CLI is ready for production use!")
    elif success_rate >= 60:
        print("\n⚠️  Scout CLI has some issues but core functionality works")
    else:
        print("\n❌ Scout CLI has significant issues that need to be addressed")

    return success_rate

async def main():
    """Run comprehensive validation tests."""
    print_header("Scout CLI - Validation & Test Suite")
    print("Testing Scout CLI installation and functionality...")

    results = []

    # Core tests
    print_header("CORE SYSTEM TESTS")
    results.append({"name": "Python Version", "status": test_python_version()})
    results.append({"name": "File Structure", "status": test_file_structure()})
    results.append({"name": "Core Dependencies", "status": test_dependencies()})
    results.append({"name": "Core Imports", "status": test_core_imports()})
    results.append({"name": "CLI Commands", "status": test_cli_commands()})
    results.append({"name": "Config File", "status": test_config_file()})
    results.append({"name": "Async Support", "status": await test_async_functionality()})

    # Advanced tests
    print_header("ADVANCED FEATURE TESTS")
    results.append({"name": "Advanced Imports", "status": test_advanced_imports()})
    available_advanced = test_advanced_dependencies()

    # Feature availability summary
    print_header("FEATURE AVAILABILITY")
    features = {
        "Core Security Scanning": True,  # Always available
        "AI - Powered Analysis": "openai" in available_advanced or "anthropic" in available_advanced,
        "Real - time Monitoring": "fastapi" in available_advanced and "redis" in available_advanced,
        "Blockchain Security": "web3" in available_advanced,
        "Web Dashboard": "fastapi" in available_advanced
    }

    for feature, available in features.items():
        print_test(feature, available)
        results.append({"name": feature, "status": available})

    # Generate final report
    success_rate = generate_summary_report(results)

    # Recommendations
    if success_rate < 100:
        print_header("RECOMMENDATIONS")
        if not any("openai" in str(r) or "anthropic" in str(r) for r in available_advanced):
            print("• Install AI dependencies: pip install openai anthropic")
        if "fastapi" not in available_advanced:
            print("• Install web dependencies: pip install -r requirements - web.txt")
        if "web3" not in available_advanced:
            print("• Install blockchain dependencies: pip install -r requirements - blockchain.txt")
        print("• Run: python install.py --profile full for complete installation")

    return success_rate >= 80

    if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        sys.exit(1)
