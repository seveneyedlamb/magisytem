import os
import customtkinter as ctk
from PIL import Image

def load_image_or_color(image_path, width, height, fallback_color):
    """
    Attempts to load an image via Pillow for CustomTkinter.
    If the image doesn't exist, returns the fallback color string instead.
    """
    if os.path.exists(image_path):
        return ctk.CTkImage(light_image=Image.open(image_path),
                            dark_image=Image.open(image_path),
                            size=(width, height)), None
    else:
        return None, fallback_color
