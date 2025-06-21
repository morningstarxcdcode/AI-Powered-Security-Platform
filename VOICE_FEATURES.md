# Scout CLI Voice Assistant Documentation

## Overview
The Scout CLI Voice Assistant provides hands-free operation of security testing tools through natural voice commands.

## Features
- 🎤 Speech recognition for voice commands
- 🗣️ Text-to-speech narration of all operations
- 📼 Recording and playback of voice sessions
- ⏸️ Pause/resume functionality
- 🔄 Repeat last message
- 💾 Session saving and documentation

## Installation
```bash
pip install -r requirements-voice.txt
```

## Usage

### Interactive Voice Mode
```bash
scout voice start
```

### Voice-Enabled Commands
```bash
scout --voice scan target.com
scout --voice ai-analysis
```

### Available Voice Commands
- "help" - Show available commands
- "run tests" - Execute security test suite
- "scan [target]" - Perform security scan
- "ai analysis" - Run AI-powered analysis
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
- pyttsx3: Text-to-speech engine
- SpeechRecognition: Speech recognition
- sounddevice: Audio device interface
- soundfile: Audio file handling
- pyaudio: Audio I/O library
