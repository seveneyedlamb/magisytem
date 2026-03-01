import customtkinter as ctk
from tkinter import font as tkfont

# Speaker color map per PRD Section 10
COLORS = {
    "MELCHIOR":  "#00d4ff",
    "BALTHASAR": "#ff8c00",
    "CASPER":    "#00ff88",
    "MAGI":      "#aaaaaa",
    "SYSTEM":    "#555566",
    "USER":      "#ffffff",
    "TOOL":      "#ffdd00",
}


class TerminalPanel(ctk.CTkFrame):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height, fg_color="#0d0d1a", corner_radius=0)
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Header bar
        header = ctk.CTkFrame(self, height=28, fg_color="#111122", corner_radius=0)
        header.pack(fill="x", side="top")
        ctk.CTkLabel(
            header, text="◈  MAGI TERMINAL  ◈",
            font=("Cascadia Mono", 11, "bold"), text_color="#00d4ff"
        ).pack(side="left", padx=12)

        # Scrollable text area
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color="#080810",
            text_color="#cccccc",
            font=("Cascadia Mono", 13),
            corner_radius=0,
            wrap="word",
            state="normal"
        )
        self.textbox.pack(fill="both", expand=True, padx=2, pady=2)

        # Configure per-speaker color tags via underlying tk widget
        for speaker, color in COLORS.items():
            self.textbox._textbox.tag_configure(f"tag_{speaker}", foreground=color)
        self.textbox._textbox.tag_configure("tag_label", foreground="#555555")

    def append_text(self, speaker: str, message: str):
        self.textbox.configure(state="normal")
        tb = self.textbox._textbox

        label = f"[{speaker}] "
        tb.insert("end", label, "tag_label")
        tag = f"tag_{speaker}" if speaker in COLORS else "tag_SYSTEM"
        tb.insert("end", message.strip() + "\n\n", tag)

        self.textbox.see("end")
        self.textbox.configure(state="normal")
