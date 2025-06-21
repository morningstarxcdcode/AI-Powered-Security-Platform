"""
Demo: VoiceGuy narrates a full Scout CLI test session, records all events, and demonstrates pause / repeat / playback.
"""
import time

from scout.voice_assistant import VoiceGuy


def run_voice_demo():
    """Run the voice demonstration."""
    script = [
        "Welcome to Scout CLI. This session will be fully narrated and recorded.",
        "Starting core security scan.",
        "Vulnerability found: SQL injection in login form.",
        "AI analysis in progress. Please wait.",
        "AI analysis complete. Executive summary: Critical vulnerabilities detected.",
        "Real-time monitoring dashboard is now live.",
        "Blockchain security analysis started.",
        "Smart contract vulnerabilities detected: Reentrancy, Oracle manipulation.",
        "Test session complete. All results have been saved."
    ]

    voice_guy = VoiceGuy()

    # Narrate and record the session
    session_dir = voice_guy.record_session(script, session_name="voice_demo")

    # Demonstrate pause and resume
    voice_guy.speak("Pausing narration for demonstration.")
    voice_guy.pause()
    time.sleep(2)
    voice_guy.resume()
    voice_guy.speak("Resuming narration after pause.")

    # Demonstrate repeat
    voice_guy.speak("This message will be repeated.")
    voice_guy.repeat()

    # List and play back a recording
    recordings = voice_guy.list_recordings()
    if recordings:
        voice_guy.speak("Playing back the first recorded event.")
        voice_guy.play_recording(0)

    print(f"Voice demo complete. Session recordings saved in: {session_dir}")


if __name__ == "__main__":
    run_voice_demo()
