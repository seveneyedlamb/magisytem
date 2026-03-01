"""
Context Bar — sits above the input field.
Lets the user load/unload .md/.txt context files and toggle Refinement Mode.
"""
import customtkinter as ctk
import os
from tkinter import filedialog


class ContextBar(ctk.CTkFrame):
    def __init__(self, master, width=480, height=42):
        super().__init__(master, width=width, height=height,
                         fg_color="#0a0a12", corner_radius=0)
        self.pack_propagate(False)
        self.grid_propagate(False)

        # State
        self._files: dict[str, str] = {}   # display_name → full_path
        self._active_file: str | None = None
        self.refinement_mode = ctk.BooleanVar(value=False)
        self.debate_mode = ctk.BooleanVar(value=False)

        # Top border
        ctk.CTkFrame(self, height=1, fg_color="#1a2a3a").pack(fill="x", side="top")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=4)

        # Label
        ctk.CTkLabel(
            row, text="CTX:", font=("Cascadia Mono", 10, "bold"),
            text_color="#445566", width=30
        ).pack(side="left")

        # File selector dropdown
        self.file_var = ctk.StringVar(value="— none —")
        self.dropdown = ctk.CTkComboBox(
            row,
            variable=self.file_var,
            values=["— none —"],
            width=160, height=26,
            font=("Cascadia Mono", 10),
            fg_color="#080810", text_color="#00d4ff",
            border_color="#1a2a3a", button_color="#111130",
            dropdown_fg_color="#0d0d20", dropdown_text_color="#00d4ff",
            command=self._on_select,
            state="readonly"
        )
        self.dropdown.pack(side="left", padx=(0, 4))

        # Add button
        ctk.CTkButton(
            row, text="+", width=26, height=26,
            font=("Cascadia Mono", 14, "bold"),
            fg_color="#001a0d", hover_color="#003322",
            text_color="#00ff88", border_color="#00ff88", border_width=1,
            corner_radius=3, command=self._add_file
        ).pack(side="left", padx=(0, 2))

        # Remove button
        ctk.CTkButton(
            row, text="✕", width=26, height=26,
            font=("Cascadia Mono", 11),
            fg_color="#1a0000", hover_color="#330000",
            text_color="#ff4444", border_color="#440000", border_width=1,
            corner_radius=3, command=self._remove_file
        ).pack(side="left", padx=(0, 12))

        # Divider
        ctk.CTkFrame(row, width=1, height=22, fg_color="#1a2a3a").pack(side="left", padx=6)

        # Refinement mode toggle
        self.refine_toggle = ctk.CTkCheckBox(
            row,
            text="Refinement",
            variable=self.refinement_mode,
            font=("Cascadia Mono", 10),
            text_color="#ff8c00",
            fg_color="#331a00",
            hover_color="#553300",
            border_color="#ff8c00",
            checkmark_color="#ff8c00",
            width=100, height=22,
            command=self._on_refinement_toggle
        )
        self.refine_toggle.pack(side="left", padx=4)

        # Status indicator
        self.status_lbl = ctk.CTkLabel(
            row, text="",
            font=("Cascadia Mono", 9), text_color="#334455",
            fg_color="transparent"
        )
        self.status_lbl.pack(side="left", padx=6)

        # Divider
        ctk.CTkFrame(row, width=1, height=22, fg_color="#1a2a3a").pack(side="left", padx=6)

        # Debate mode toggle
        self.debate_toggle = ctk.CTkCheckBox(
            row,
            text="Debate",
            variable=self.debate_mode,
            font=("Cascadia Mono", 10),
            text_color="#00d4ff",
            fg_color="#001a33",
            hover_color="#003366",
            border_color="#00d4ff",
            checkmark_color="#00d4ff",
            width=80, height=22,
            command=self._on_debate_toggle
        )
        self.debate_toggle.pack(side="left", padx=4)

        # Divider
        ctk.CTkFrame(row, width=1, height=22, fg_color="#1a2a3a").pack(side="left", padx=6)

        # Git mode toggle
        self.git_toggle = ctk.CTkCheckBox(
            row,
            text="Git",
            variable=self.git_mode,
            font=("Cascadia Mono", 10),
            text_color="#00ff88",
            fg_color="#001a0d",
            hover_color="#003322",
            border_color="#00ff88",
            checkmark_color="#00ff88",
            width=60, height=22,
            command=self._on_git_toggle
        )
        self.git_toggle.pack(side="left", padx=4)

    # ── File management ─────────────────────────────────────────────────────

    def _add_file(self):
        path = filedialog.askopenfilename(
            title="Load Context File",
            filetypes=[("Markdown / Text", "*.md *.txt"), ("All files", "*.*")],
            initialdir=os.path.join(os.path.dirname(__file__), "..", "prompts")
        )
        if not path:
            return
        name = os.path.basename(path)
        self._files[name] = path
        self._refresh_dropdown(name)

    def _remove_file(self):
        sel = self.file_var.get()
        if sel in self._files:
            del self._files[sel]
            self._active_file = None
            self._refresh_dropdown("— none —")

    def _refresh_dropdown(self, select: str):
        values = ["— none —"] + list(self._files.keys())
        self.dropdown.configure(values=values)
        self.file_var.set(select)
        self._on_select(select)

    def _on_select(self, value):
        self._active_file = self._files.get(value)
        if self._active_file:
            self.status_lbl.configure(text=f"● {value[:20]}", text_color="#00d4ff")
        else:
            self.status_lbl.configure(text="", text_color="#334455")

    def _on_refinement_toggle(self):
        if self.refinement_mode.get():
            self.status_lbl.configure(text="◈ Refine ON", text_color="#ff8c00")
        else:
            self._on_select(self.file_var.get())  # restore file status

    def _on_debate_toggle(self):
        if self.debate_mode.get():
            self.debate_toggle.configure(text="Debate ●")
        else:
            self.debate_toggle.configure(text="Debate")

    # ── Public API ───────────────────────────────────────────────────────────

    def get_context_text(self) -> str:
        """Returns the active context file content, or empty string."""
        if not self._active_file:
            return ""
        try:
            with open(self._active_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""

    def is_refinement_mode(self) -> bool:
        return self.refinement_mode.get()

    def is_debate_mode(self) -> bool:
        return self.debate_mode.get()

    def is_git_mode(self) -> bool:
        return self.git_mode.get()
