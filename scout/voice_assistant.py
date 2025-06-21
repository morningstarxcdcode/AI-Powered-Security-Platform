"""
Scout Voice Assistant Module
Provides voice interaction capabilities for the Scout CLI tool.
"""

import json
import os
import time
from typing import Optional

from scout.logging import log_error, log_info, log_warning

# Voice recognition dependencies
try:
    import pyttsx3
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    sr = None
    pyttsx3 = None
    VOICE_AVAILABLE = False


class VoiceAssistant:
    """Advanced voice assistant for Scout CLI."""

    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = sr.Microphone() if sr else None
        self.tts_engine = None
        self.session_events = []
        self.session_id = None

        if pyttsx3:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_voice()
            except Exception as e:
                log_error(f"Failed to initialize TTS engine: {e}")
                self.tts_engine = None

    def _configure_voice(self):
        """Configure voice settings."""
        if not self.tts_engine:
            return

        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break

            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)

        except Exception as e:
            log_error(f"Error configuring voice: {e}")

    def speak(self, text: str, record: bool = True, filename: str = None):
        """Convert text to speech."""
        if not text:
            return

        try:
            if record:
                self.session_events.append({
                    'type': 'speak',
                    'text': text,
                    'timestamp': time.time()
                })

            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                log_info(f"Voice output: {text[:50]}...")
            else:
                log_info(f"🗣️ Voice: {text}")

        except Exception as e:
            log_error(f"Error in text-to-speech: {e}")
            log_info(f"🗣️ Voice: {text}")

    def listen(self,
               timeout: int = 5,
               phrase_time_limit: int = 10
               ) -> Optional[str]:
        """Listen for user voice input and return recognized text."""
        if not VOICE_AVAILABLE:
            return None

        try:
            with self.microphone as source:
                log_info("Listening for voice input...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            text = self.recognizer.recognize_google(audio)
            log_info(f"Voice input recognized: {text}")

            self.session_events.append({
                'type': 'listen',
                'text': text,
                'timestamp': time.time()
            })

            return text

        except sr.WaitTimeoutError:
            log_warning("Voice input timeout")
            return None
        except sr.UnknownValueError:
            log_warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            log_error(f"Voice recognition error: {e}")
            return None
        except Exception as e:
            log_error(f"Unexpected error in voice recognition: {e}")
            return None

    def start_session(self, session_id: str = None):
        """Start a new voice session."""
        self.session_id = session_id or f"voice_session_{int(time.time())}"
        self.session_events = []
        log_info(f"Started voice session: {self.session_id}")

    def end_session(self):
        """End current voice session and save recordings."""
        if not self.session_id:
            return

        try:
            # Create session directory
            session_dir = os.path.join("voice_recordings", self.session_id)
            os.makedirs(session_dir, exist_ok=True)

            # Save session events
            events_file = os.path.join(session_dir, "session_events.json")
            with open(events_file, 'w') as f:
                json.dump(self.session_events, f, indent=2)

            log_info(f"Voice session saved: {session_dir}")

        except Exception as e:
            log_error(f"Error saving voice session: {e}")
        finally:
            self.session_id = None
            self.session_events = []

    def handle_voice_command(self, command: str) -> str:
        """Process voice command and return response."""
        if not command:
            return "I didn't catch that. Could you please repeat?"

        command = command.lower().strip()

        # Basic command handling
        if any(word in command for word in ['help', 'what can you do']):
            return self._get_help_response()
        elif any(word in command for word in ['scan', 'start scan']):
            return "To start a scan, please specify a target URL or use the scan command."
        elif any(word in command for word in ['report', 'show report']):
            return "You can generate reports using the report command with various formats."
        elif any(word in command for word in ['exit', 'quit', 'goodbye']):
            return "Goodbye! Thank you for using Scout voice assistant."
        else:
            return "I understand you said: " + command + ". How can I help you with that?"

    def _get_help_response(self) -> str:
        """Get help response for voice commands."""
        return """I'm Scout's voice assistant. I can help you with:
        - Starting security scans
        - Generating reports
        - Explaining vulnerabilities
        - Navigating Scout features

        Try saying things like 'start a scan', 'show report', or 'explain XSS'."""


class VoiceCommandInterface:
    """Interface for voice-controlled Scout operations."""

    def __init__(self):
        self.assistant = VoiceAssistant() if VOICE_AVAILABLE else None
        self.active = False

    def start_voice_mode(self):
        """Start interactive voice mode."""
        if not VOICE_AVAILABLE:
            log_info("Voice features not available. Please install speech_recognition and pyttsx3.")
            return

        if not self.assistant:
            log_info("Voice assistant not initialized.")
            return

        self.active = True
        self.assistant.start_session()
        self.assistant.speak("Scout voice assistant activated. How can I help you?")

        try:
            while self.active:
                command = self.assistant.listen()
                if command:
                    if 'exit' in command.lower() or 'quit' in command.lower():
                        self.assistant.speak("Goodbye!")
                        break

                    response = self.assistant.handle_voice_command(command)
                    self.assistant.speak(response)

        except KeyboardInterrupt:
            self.assistant.speak("Voice mode interrupted.")
        finally:
            self.assistant.end_session()
            self.active = False

    def stop_voice_mode(self):
        """Stop voice mode."""
        self.active = False


# Global voice interface
voice_interface = VoiceCommandInterface()


def speak_if_available(text: str):
    """Convenience function to speak text if voice is available."""
    if VOICE_AVAILABLE and voice_interface.assistant:
        voice_interface.assistant.speak(text, record=False)
    else:
        log_info(f"🗣️ Voice: {text}")


def start_voice_mode():
    """Start voice command mode."""
    voice_interface.start_voice_mode()


def get_assistant() -> Optional[VoiceAssistant]:
    """Get the voice assistant instance."""
    return voice_interface.assistant if voice_interface else None


# Legacy compatibility
VoiceGuy = VoiceAssistant  # For backward compatibility
