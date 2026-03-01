import sys
import os

# Ensure core is importable
sys.path.insert(0, os.path.abspath('.'))

from core.config import CONFIG

def test_config():
    assert CONFIG['MELCHIOR_VOICE'] == 'Hugo'
    assert CONFIG['LM_STUDIO_URL'] == 'http://localhost:1234/v1'
    assert CONFIG['VOICE_OUTPUT_DEFAULT'] == True
    assert CONFIG['MAX_DEBATE_ROUNDS'] == 3
    assert CONFIG['MELCHIOR_INTENSITY'] == 0.7
    print("Config works!")

if __name__ == "__main__":
    test_config()
