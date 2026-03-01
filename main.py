import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from ui.app import MAGIApp

if __name__ == "__main__":
    app = MAGIApp()
    app.run()
