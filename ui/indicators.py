import customtkinter as ctk
from PIL import Image
import os

FRAME_INTERVAL = 80  # ms between animation frames


class AIIndicator(ctk.CTkFrame):
    def __init__(self, master, name: str, width=150, height=150, color="#ffffff"):
        super().__init__(master, width=width, height=height, corner_radius=0, fg_color="transparent")
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.name = name
        self.color = color
        self._after_id = None
        self._frame_idx = 0

        # Load all frame sequences
        n = name.lower()
        self._frames = {
            "idle":     self._load_frames(f"images/{n}_idle.png"),
            "active":   self._load_frames(f"images/{n}_active.png"),
            "thinking": self._load_sequence(f"images/{n}_thinking_", 12),
            "speaking": self._load_sequence(f"images/{n}_speaking_", 16),
        }

        self.label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.set_state("idle")

    def _load_frames(self, path: str) -> list:
        if os.path.exists(path):
            img = Image.open(path).convert("RGB")
            return [ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))]
        # Fallback: colored rectangle
        return [None]

    def _load_sequence(self, prefix: str, count: int) -> list:
        frames = []
        for i in range(count):
            path = f"{prefix}{i:02d}.png"
            if os.path.exists(path):
                img = Image.open(path).convert("RGB")
                frames.append(ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150)))
        return frames if frames else [None]

    def set_state(self, state: str):
        """States: idle, active, thinking, speaking"""
        self._stop_animation()
        frames = self._frames.get(state, self._frames["idle"])

        if len(frames) == 1:
            self._show_frame(frames[0])
        else:
            self._frame_idx = 0
            self._state_frames = frames
            self._animate()

    def _show_frame(self, frame):
        if frame:
            self.label.configure(image=frame, text="")
        else:
            self.label.configure(image=None, text=self.name, text_color=self.color,
                                  font=("Courier New", 10, "bold"))

    def _animate(self):
        frames = self._state_frames
        self._show_frame(frames[self._frame_idx % len(frames)])
        self._frame_idx += 1
        self._after_id = self.after(FRAME_INTERVAL, self._animate)

    def _stop_animation(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
