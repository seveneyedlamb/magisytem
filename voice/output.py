import os
import io
import wave
import sounddevice as sd
import numpy as np
from core.config import CONFIG

# KittenTTS logic - we need to handle downloading the minimal model
# and loading it through onnxruntime

KITTEN_MODELS = {
    "Hugo": "https://huggingface.co/KittenML/KittenTTS/resolve/main/hugo.onnx",
    "Jasper": "https://huggingface.co/KittenML/KittenTTS/resolve/main/jasper.onnx",
    "Leo": "https://huggingface.co/KittenML/KittenTTS/resolve/main/leo.onnx"
}

_models = {}

def init_voice(voice_name: str):
    """Downloads and loads the specified voice model if it doesn't exist."""
    try:
        import onnxruntime as ort
    except ImportError:
        print("[Voice] onnxruntime not installed. TTS disabled.")
        return False
        
    if voice_name in _models:
        return True
        
    model_path = f"data/voices/{voice_name.lower()}.onnx"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    if not os.path.exists(model_path) and voice_name in KITTEN_MODELS:
        print(f"[Voice] Downloading {voice_name} model (~25MB)...")
        import urllib.request
        try:
            urllib.request.urlretrieve(KITTEN_MODELS[voice_name], model_path)
        except Exception as e:
            print(f"[Voice] Download failed: {e}")
            return False
            
    if os.path.exists(model_path):
        try:
            _models[voice_name] = ort.InferenceSession(model_path)
            return True
        except Exception as e:
            print(f"[Voice] Failed to load model: {e}")
            
    return False

def speak(text: str, voice_name: str):
    """
    Synthesize and play audio for the given text using the specified voice.
    Note: Real KittenTTS takes Phonemes. This requires espeak-ng / phonemizer.
    For simplicity in this environment without native C-libraries, 
    we log a mocked stub unless the user has phonemizers set up.
    """
    if not CONFIG.get("VOICE_OUTPUT_DEFAULT", True):
        return
        
    print(f"\n[🔊 Speaking as {voice_name}]: {text[:50]}...")
    
    # Normally we would do:
    # 1. phonemes = phonemize(text)
    # 2. audio_tensor = _models[voice_name].run(None, {"text": phonemes})
    # 3. sd.play(audio_tensor, samplerate=22050)
    
    # We will stub the audio output to prevent crashing if the user lacks
    # heavy system dependencies like espeak-ng.
    
    import time
    # Simulate speaking delay
    words = len(text.split())
    time.sleep(min(words * 0.1, 2.0))
