import sys
import os

sys.path.insert(0, os.path.abspath('.'))

try:
    from voice.input import listen_for_input
    from voice.output import speak, init_voice
    
    print("--- Testing Phase 4 Voice Subsystem ---")
    
    print("\n[TEST 1] Testing Voice Output Stub (Hugo)")
    init_voice("Hugo")
    speak("This is a functional test of the audio abstraction layer.", "Hugo")
    
    print("\n[TEST 2] Testing Microphone Configuration")
    print("If you see [Microphone timeout], recording works but no speech was detected.")
    print("Listening for up to 3 seconds...")
    res = listen_for_input(timeout=3, phrase_time_limit=3)
    print(f"Result: {res}")
    print("\nVoice integrations succeed.")
    
except Exception as e:
    print(f"Voice test failed with dependency or init error: {e}")
