#!/usr/bin/env python3
"""
Scout CLI Voice Test Runner
Comprehensive testing and demonstration of voice assistant capabilities.
"""
import subprocess
import sys
import time
from pathlib import Path


def test_voice_dependencies():
    """Test if voice dependencies are installed."""
    print("🔧 Testing voice dependencies...")

    dependencies = [
        ("pyttsx3", "Text-to-speech engine"),
        ("speech_recognition", "Speech recognition"),
        ("sounddevice", "Audio device interface"),
        ("soundfile", "Audio file handling"),
        ("pyaudio", "Audio I/O")
    ]

    missing = []
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {desc} ({dep})")
        except ImportError:
            print(f"❌ {desc} ({dep}) - Missing")
            missing.append(dep)

    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("🔧 Install with: pip install -r requirements - voice.txt")
        return False

    print("✅ All voice dependencies available!")
    return True

    """Test voice assistant functionality."""
    print("\n🎤 Testing Voice Assistant...")

    try:
        from scout.voice_assistant import VoiceGuy, voice_interface

        if not voice_interface.is_available():
            print("❌ Voice interface not available")
            return False

        # Test basic functionality
        voice = VoiceGuy()

        print("🗣️ Testing text - to - speech...")
        voice.speak("Voice assistant test successful. All systems operational.", record=False)

        print("✅ Voice assistant test completed!")
        return True

    except Exception as e:
        print(f"❌ Voice assistant test failed: {e}")
        return False

    """Test CLI voice integration."""
    print("\n🖥️ Testing CLI Voice Integration...")

    try:
        # Test voice command availability
        result = subprocess.run(
            [sys.executable, "-m", "scout.cli", "voice", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and "voice" in result.stdout.lower():
            print("✅ Voice commands available in CLI")
            return True
        else:
            print("❌ Voice commands not properly integrated")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False

    """Run voice demonstration."""
    print("\n🎭 Running Voice Demo...")

    try:
        from scout.voice_assistant import VoiceGuy

        voice = VoiceGuy()

        demo_script = [
            "Welcome to Scout CLI Voice Assistant demonstration.",
            "I am your security testing companion.",
            "I can narrate all security tests and respond to voice commands.",
            "You can say commands like: Help me run all tests.",
            "Or: Scan a target for vulnerabilities.",
            "Or: Start AI analysis.",
            "I will record all our interactions for later review.",
            "Voice demonstration complete. Thank you for testing Scout CLI."
        ]

        print("🎬 Starting voice demo narration...")
        session_dir = voice.record_session(demo_script, "voice_test_demo")

        print(f"✅ Demo completed! Session saved to: {session_dir}")
        return True

    except Exception as e:
        print(f"❌ Voice demo failed: {e}")
        return False

    """Test voice command recognition (simulated)."""
    print("\n🎯 Testing Voice Commands...")

    test_commands = [
        "help",
        "run tests",
        "scan target",
        "ai analysis",
        "blockchain scan",
        "real time monitor",
        "status",
        "pause",
        "resume",
        "repeat"
    ]

    try:
        from scout.voice_assistant import VoiceGuy

        voice = VoiceGuy()

        print("🧪 Testing command recognition logic...")
        for cmd in test_commands:
            # Simulate command processing
            print(f"  🔍 Testing: '{cmd}'")
            voice._process_voice_command(cmd)
            time.sleep(0.5)

        print("✅ Voice command tests completed!")
        return True

    except Exception as e:
        print(f"❌ Voice command test failed: {e}")
        return False

    """Generate voice assistant documentation."""
    print("\n📝 Generating Voice Documentation...")

    doc_content = """# Scout CLI Voice Assistant Documentation

## Overview
The Scout CLI Voice Assistant provides hands - free operation of security testing tools through natural voice commands.

## Features
- 🎤 Speech recognition for voice commands
- 🗣️ Text - to - speech narration of all operations
- 📼 Recording and playback of voice sessions
- ⏸️ Pause / resume functionality
- 🔄 Repeat last message
- 💾 Session saving and documentation

## Installation
```bash
pip install -r requirements - voice.txt
```

## Usage

### Interactive Voice Mode
```bash
scout voice start
```

### Voice - Enabled Commands
```bash
scout --voice scan target.com
scout --voice ai - analysis
```

### Available Voice Commands
    - "help" - Show available commands
    - "run tests" - Execute security test suite
    - "scan [target]" - Perform security scan
    - "ai analysis" - Run AI - powered analysis
    - "blockchain scan" - Analyze smart contracts
    - "real time monitor" - Start live monitoring
    - "pause" - Pause voice assistant
    - "resume" - Resume voice assistant
    - "repeat" - Repeat last message
    - "status" - Show current status
    - "stop listening" - Exit voice mode

### Testing Voice Assistant
```bash
scout voice test
scout voice demo
scout voice status
```

## Voice Session Management
All voice interactions are automatically recorded and saved to the `voice_recordings/` directory with:
- Audio files of spoken messages
- JSON event logs
- Markdown session summaries

## Troubleshooting
- Ensure microphone permissions are granted
- Check audio device configuration
- Verify internet connection for speech recognition
- Calibrate microphone in noisy environments

## Dependencies
- pyttsx3: Text - to - speech engine
- SpeechRecognition: Speech recognition
- sounddevice: Audio device interface
- soundfile: Audio file handling
- pyaudio: Audio I / O library
"""

    doc_file = Path("VOICE_FEATURES.md")
    doc_file.write_text(doc_content)
    print(f"✅ Documentation generated: {doc_file}")

    """Run comprehensive voice assistant tests."""
    print("🎤 Scout CLI Voice Assistant Test Suite")
    print("=" * 50)

    tests = [
        ("Dependencies", test_voice_dependencies),
        ("Voice Assistant", test_voice_assistant),
        ("CLI Integration", test_cli_voice_integration),
        ("Voice Commands", test_voice_commands),
        ("Voice Demo", run_voice_demo)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Generate documentation
    generate_voice_documentation()

    # Summary
    print("\n" + "=" * 50)
    print("🏁 Voice Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All voice assistant tests passed!")
        print("🗣️ Voice assistant is ready for production use!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    print("\n📋 Next Steps:")
    print("1. Run: scout voice start")
    print("2. Say: 'help me run all tests'")
    print("3. Enjoy hands - free security testing!")

    

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
