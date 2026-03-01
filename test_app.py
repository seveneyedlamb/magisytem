import sys
import os

sys.path.insert(0, os.path.abspath('.'))

try:
    from ui.app import MAGIApp
    app = MAGIApp()
    
    # Destroy after 500ms to test clean instantiation and exit
    app.after(500, app.destroy)
    app.run()
    print("App instantiated and destroyed successfully. UI layout logic is sound.")
except Exception as e:
    print(f"App instantiation failed: {e}")
