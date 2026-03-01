import speech_recognition as sr

def listen_for_input(timeout=5, phrase_time_limit=15) -> str:
    """
    Listens to the default microphone and returns transcribed text.
    Returns an empty string or error message if failed.
    """
    try:
        import pyaudio
    except ImportError:
        return "[Error: PyAudio not installed. Please install PyAudio to use voice input.]"
        
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen to the user
            audio = recognizer.listen(
                source, 
                timeout=timeout, 
                phrase_time_limit=phrase_time_limit
            )
            
        # Transcribe using Google's free API
        text = recognizer.recognize_google(audio)
        return text
        
    except sr.WaitTimeoutError:
        return "[Microphone timeout - No speech detected]"
    except sr.UnknownValueError:
        return "[Speech unintelligible]"
    except sr.RequestError as e:
        return f"[Speech recognition service error: {e}]"
    except Exception as e:
        return f"[Microphone error: {str(e)}]"
        
    except sr.WaitTimeoutError:
        return "[Microphone timeout - No speech detected]"
    except sr.UnknownValueError:
        return "[Speech unintelligible]"
    except sr.RequestError as e:
        return f"[Speech recognition service error: {e}]"
    except Exception as e:
        return f"[Microphone error: {str(e)}]"
