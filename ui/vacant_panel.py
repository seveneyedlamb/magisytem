import customtkinter as ctk
import threading


class VacantPanel(ctk.CTkFrame):
    def __init__(self, master, width, height):
        super().__init__(master, width=width, height=height, fg_color="#0d0d1a", corner_radius=0)
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Top border
        ctk.CTkFrame(self, height=1, fg_color="#1a2a3a").pack(fill="x", side="top")

        # Mic button
        self.mic_btn = ctk.CTkButton(
            self, text="🎤", width=44, height=44,
            font=("Arial", 20), fg_color="#111122",
            hover_color="#1a1a44", border_color="#223355",
            border_width=1, corner_radius=5,
            command=self._on_mic_click
        )
        self.mic_btn.place(x=12, y=64)

        # Text input
        self.input_field = ctk.CTkTextbox(
            self, width=340, height=86,
            fg_color="#080810", text_color="#00d4ff",
            font=("Cascadia Mono", 13), corner_radius=4,
            border_color="#1a2a3a", border_width=1
        )
        self.input_field.place(x=64, y=42)

        # Enter = newline in the field; Ctrl+Enter or Shift+Enter = submit
        self.input_field.bind("<Return>", self._on_enter)
        self.input_field.bind("<Control-Return>", self._on_submit)
        self.input_field.bind("<Shift-Return>", self._on_submit)

        # Tool status label
        self.status_label = ctk.CTkLabel(
            self, text="○ Ready",
            font=("Courier New", 10), text_color="#333355",
            fg_color="transparent"
        )
        self.status_label.place(x=64, y=136)

        # Send button
        self.send_btn = ctk.CTkButton(
            self, text="►", width=54, height=86,
            font=("Arial", 22, "bold"),
            fg_color="#003344", hover_color="#00d4ff",
            text_color="#00d4ff", corner_radius=4,
            border_color="#00d4ff", border_width=1
        )
        self.send_btn.place(x=412, y=42)

    def _on_enter(self, event):
        """Return key inserts a newline — does not submit."""
        self.input_field.insert("insert", "\n")
        return "break"  # prevent default

    def _on_submit(self, event):
        """Ctrl+Enter / Shift+Enter submits the query."""
        if self.send_btn.cget("state") != "disabled":
            self.send_btn.invoke()
        return "break"

    def _on_mic_click(self):
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        from voice.input import listen_for_input
        self.input_field.delete("0.0", "end")
        self.input_field.insert("0.0", "Listening...")
        self.mic_btn.configure(fg_color="#330000", border_color="#ff3333")
        text = listen_for_input()
        self.mic_btn.configure(fg_color="#111122", border_color="#223355")
        self.input_field.delete("0.0", "end")
        if text and not text.startswith("["):
            self.input_field.insert("0.0", text)
