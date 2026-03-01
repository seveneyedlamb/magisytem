import customtkinter as ctk
from core.config import CONFIG


class ControlsPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Address dropdown
        self.address_var = ctk.StringVar(value="ALL")
        ctk.CTkOptionMenu(
            self,
            values=["ALL", "MELCHIOR", "BALTHASAR", "CASPER"],
            variable=self.address_var,
            width=140,
            fg_color="#1a1a2e",
            button_color="#003344",
            button_hover_color="#00d4ff",
            text_color="#00d4ff",
            font=("Courier New", 11, "bold")
        ).pack(side="left", padx=6)

        # TTS toggle — default from config
        voice_on = CONFIG.get("VOICE_OUTPUT_DEFAULT", "on")
        self.voice_var = ctk.BooleanVar(value=(str(voice_on).lower() not in ("off", "false", "0")))
        ctk.CTkSwitch(
            self,
            text="🔊",
            variable=self.voice_var,
            onvalue=True,
            offvalue=False,
            progress_color="#00d4ff",
            button_color="#00d4ff",
            width=48
        ).pack(side="left", padx=6)

        # Reset button (NeoVand pattern)
        self.reset_btn = ctk.CTkButton(
            self,
            text="RESET",
            width=70,
            height=28,
            fg_color="#1a0000",
            hover_color="#330000",
            border_color="#ff3333",
            border_width=1,
            text_color="#ff3333",
            font=("Courier New", 10, "bold"),
            corner_radius=3
        )
        self.reset_btn.pack(side="left", padx=6)
