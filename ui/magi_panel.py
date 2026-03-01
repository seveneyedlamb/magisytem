import customtkinter as ctk
import tkinter as tk
from ui.indicators import AIIndicator
from ui.image_loader import load_image_or_color


class MAGIPanel(ctk.CTkFrame):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height, fg_color="#0a0a0a", corner_radius=0)
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Background image
        self.bg_image, _ = load_image_or_color("images/magi_background.png", width, height, "#0d0d1a")
        if self.bg_image:
            bg_label = ctk.CTkLabel(self, text="", image=self.bg_image)
            bg_label.place(x=0, y=0)

        # Canvas for connector lines behind indicators
        self.canvas = tk.Canvas(
            self, width=width, height=height,
            bg="#0a0a0a", highlightthickness=0
        )
        self.canvas.place(x=0, y=0)
        self._draw_connections()

        # AI Indicators — exact PRD coordinates
        self.melchior = AIIndicator(self, "MELCHIOR", color="#00d4ff")
        self.melchior.place(x=285, y=80)

        self.casper = AIIndicator(self, "CASPER", color="#00ff88")
        self.casper.place(x=120, y=400)

        self.balthasar = AIIndicator(self, "BALTHASAR", color="#ff8c00")
        self.balthasar.place(x=450, y=400)

        # MAGI hub
        hub_img, _ = load_image_or_color("images/magi_hub.png", 100, 100, None)
        if hub_img:
            hub_label = ctk.CTkLabel(self, text="", image=hub_img)
            hub_label.place(x=310, y=280)
        else:
            hub_label = ctk.CTkLabel(
                self, text="◈", text_color="#555555",
                font=("Courier New", 36, "bold"), fg_color="transparent"
            )
            hub_label.place(x=340, y=295)

        # Controls bar
        from ui.controls import ControlsPanel
        self.controls = ControlsPanel(self)
        self.controls.place(x=200, y=623)

        # Wire address change to indicator dimming
        self.controls.address_var.trace_add("write", self._on_address_change)

    def _draw_connections(self):
        """Draw dim connector lines between indicators and hub in PRD triangle formation."""
        # Node centers (indicator x + 75, y + 75 for 150x150 widget)
        melchior_c = (285 + 75, 80 + 75)   # (360, 155)
        casper_c   = (120 + 75, 400 + 75)  # (195, 475)
        balthasar_c = (450 + 75, 400 + 75) # (525, 475)
        hub_c      = (310 + 50, 280 + 50)  # (360, 330)

        line_opts = {"fill": "#1a2a3a", "width": 1, "dash": (4, 4)}

        self.canvas.create_line(*melchior_c, *hub_c, **line_opts)
        self.canvas.create_line(*hub_c, *casper_c, **line_opts)
        self.canvas.create_line(*hub_c, *balthasar_c, **line_opts)

    def _on_address_change(self, *args):
        mode = self.controls.address_var.get()
        active = ["MELCHIOR", "BALTHASAR", "CASPER"] if mode == "ALL" else [mode]
        for name, widget in [("MELCHIOR", self.melchior), ("CASPER", self.casper), ("BALTHASAR", self.balthasar)]:
            widget.set_state("active" if name in active else "idle")
