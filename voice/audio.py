"""
Audio device inspection utility.
Separate from voice/input.py and voice/output.py — device enumeration only.
"""

def list_devices() -> list:
    """
    Returns a list of available audio device dicts with index and name.
    Returns empty list if sounddevice is not installed.
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        return [{"index": i, "name": d["name"], "inputs": d["max_input_channels"], "outputs": d["max_output_channels"]}
                for i, d in enumerate(devices)]
    except Exception:
        return []

def get_default_input() -> int:
    """Returns the index of the default input device, or -1 on error."""
    try:
        import sounddevice as sd
        return sd.default.device[0]
    except Exception:
        return -1

def get_default_output() -> int:
    """Returns the index of the default output device, or -1 on error."""
    try:
        import sounddevice as sd
        return sd.default.device[1]
    except Exception:
        return -1
