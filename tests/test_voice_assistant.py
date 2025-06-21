"""
Test Scout Voice Assistant functionality
"""
from unittest.mock import Mock, patch

from scout.voice_assistant import VoiceAssistant, VoiceCommandInterface


class TestVoiceAssistant:
    """Test voice assistant functionality."""

    @patch('scout.voice_assistant.VOICE_AVAILABLE', True)
    @patch('scout.voice_assistant.sr')
    @patch('scout.voice_assistant.pyttsx3')
    def test_voice_assistant_initialization(self, mock_pyttsx3, mock_sr):
        """Test voice assistant initialization."""
        mock_sr.Recognizer.return_value = Mock()
        mock_sr.Microphone.return_value = Mock()
        mock_pyttsx3.init.return_value = Mock()
        
        assistant = VoiceAssistant()
        assert assistant.recognizer is not None
        assert assistant.microphone is not None

    @patch('scout.voice_assistant.VOICE_AVAILABLE', False)
    def test_voice_assistant_no_dependencies(self):
        """Test voice assistant without dependencies."""
        assistant = VoiceAssistant()
        assert assistant.recognizer is None
        assert assistant.microphone is None

    def test_handle_voice_command_help(self):
        """Test voice command handling for help."""
        assistant = VoiceAssistant()
        response = assistant.handle_voice_command("help")
        assert "Scout's voice assistant" in response
        assert "security scans" in response

    def test_handle_voice_command_scan(self):
        """Test voice command handling for scan."""
        assistant = VoiceAssistant()
        response = assistant.handle_voice_command("start scan")
        assert "scan" in response.lower()
        assert "target" in response.lower()

    def test_handle_voice_command_report(self):
        """Test voice command handling for report."""
        assistant = VoiceAssistant()
        response = assistant.handle_voice_command("show report")
        assert "report" in response.lower()

    def test_handle_voice_command_exit(self):
        """Test voice command handling for exit."""
        assistant = VoiceAssistant()
        response = assistant.handle_voice_command("exit")
        assert "goodbye" in response.lower()

    def test_session_management(self):
        """Test voice session management."""
        assistant = VoiceAssistant()
        
        # Start session
        assistant.start_session("test_session")
        assert assistant.session_id == "test_session"
        assert len(assistant.session_events) == 0
        
        # Add some events
        assistant.session_events.append({
            'type': 'test',
            'data': 'test_data'
        })
        
        # End session should reset
        assistant.end_session()
        assert assistant.session_id is None
        assert len(assistant.session_events) == 0

    @patch('scout.voice_assistant.VOICE_AVAILABLE', False)
    def test_voice_command_interface_no_voice(self):
        """Test voice command interface without voice support."""
        interface = VoiceCommandInterface()
        assert interface.assistant is None
        
        # Should handle gracefully
        interface.start_voice_mode()  # Should print message and return
