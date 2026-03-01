import os

def load_config(config_path="config.txt"):
    """
    Loads key-value pairs from the specified config file.
    Returns a dictionary of configuration settings.
    """
    config = {}
    if not os.path.exists(config_path):
        return config
        
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignore comments and empty lines
            if not line or line.startswith("#"):
                continue
                
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Basic type conversions
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.lower() == "on":
                    value = True
                elif value.lower() == "off":
                    value = False
                else:
                    try:
                        if "." in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass # Keep as string
                        
                config[key] = value
                
    return config

# Load config globally so other modules can import it easily
if os.path.exists("config.txt"):
    CONFIG = load_config("config.txt")
else:
    CONFIG = {}
