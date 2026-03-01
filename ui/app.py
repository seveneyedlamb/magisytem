import customtkinter as ctk
import threading
import asyncio
from ui.magi_panel import MAGIPanel
from ui.terminal_panel import TerminalPanel
from ui.vacant_panel import VacantPanel
from ui.context_bar import ContextBar
from ui.layout import apply_layout
from core.orchestrator import MAGIOrchestrator
from core.config import CONFIG


class MAGIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MAGI System")
        self.geometry("1200x700")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0a0a0a")

        self.magi_panel = MAGIPanel(self, width=720, height=700)
        self.terminal_panel = TerminalPanel(self, width=480, height=483)
        self.context_bar = ContextBar(self, width=480, height=42)
        self.vacant_panel = VacantPanel(self, width=480, height=175)
        apply_layout(self, self.magi_panel, self.terminal_panel, self.context_bar, self.vacant_panel)

        self.orchestrator = MAGIOrchestrator()
        self._last_response = ""  # tracks last MAGI output for /memory command

        # Wire send button
        self.vacant_panel.send_btn.configure(command=self.submit_query)

        # Wire reset button (NeoVand pattern)
        self.magi_panel.controls.reset_btn.configure(command=self._on_reset)

        # Wire address selector to indicator dimming
        self.magi_panel.controls.address_var.trace_add("write", self._on_address_change)

        self.terminal_panel.append_text("SYSTEM", "MAGI SYSTEM ONLINE. All systems nominal.")

    def _on_reset(self):
        self.orchestrator.reset_history()
        self.terminal_panel.textbox.configure(state="normal")
        self.terminal_panel.textbox._textbox.delete("1.0", "end")
        self.terminal_panel.append_text("SYSTEM", "History cleared. MAGI systems reset.")

    def _on_address_change(self, *args):
        from ui.animations import stop_pulse
        mode = self.magi_panel.controls.address_var.get()
        indicators = {
            "MELCHIOR":  (self.magi_panel.melchior,  "#00d4ff"),
            "BALTHASAR": (self.magi_panel.balthasar, "#ff8c00"),
            "CASPER":    (self.magi_panel.casper,    "#00ff88"),
        }
        active = list(indicators.keys()) if mode == "ALL" else [mode]
        for name, (widget, _) in indicators.items():
            widget.set_state("active" if name in active else "idle")

    def submit_query(self):
        text = self.vacant_panel.input_field.get("0.0", "end").strip()
        if not text:
            return
        self.vacant_panel.input_field.delete("0.0", "end")

        # /memory slash command — commit last response to pinned memory
        if text.strip().lower().startswith("/memory"):
            note = text.strip()[7:].strip()  # optional annotation after /memory
            self._commit_memory(note)
            return

        self.terminal_panel.append_text("USER", text)
        self.vacant_panel.send_btn.configure(state="disabled")
        address = self.magi_panel.controls.address_var.get()
        context_text = self.context_bar.get_context_text()
        refinement = self.context_bar.is_refinement_mode()
        debate = self.context_bar.is_debate_mode()
        git = self.context_bar.is_git_mode()
        self._set_thinking(address)
        threading.Thread(
            target=self._run_thread,
            args=(text, address, context_text, refinement, debate, git),
            daemon=True
        ).start()

    def _set_thinking(self, address: str):
        indicators = {
            "MELCHIOR":  self.magi_panel.melchior,
            "BALTHASAR": self.magi_panel.balthasar,
            "CASPER":    self.magi_panel.casper,
        }
        active = list(indicators.keys()) if address == "ALL" else [address]
        for name, widget in indicators.items():
            widget.set_state("thinking" if name in active else "idle")

    def _clear_thinking(self):
        for widget in [self.magi_panel.melchior, self.magi_panel.balthasar, self.magi_panel.casper]:
            widget.set_state("idle")

    def _run_thread(self, text, address, context_text="", refinement=False, debate=False, git=False):
        def log(msg):
            self.after(0, lambda m=msg: self.terminal_panel.append_text("SYSTEM", m))
        def tool_log(msg):
            self.after(0, lambda m=msg: self.terminal_panel.append_text("TOOL", m))
        def stats_log(msg):
            self.after(0, lambda m=msg: self.terminal_panel.append_text("SYSTEM", m))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                self.orchestrator.process_query(
                    text, address_mode=address,
                    status_callback=log, tool_callback=tool_log,
                    stats_callback=stats_log,
                    context_text=context_text,
                    refinement_mode=refinement,
                    debate_mode=debate
                )
            )
            self.after(0, lambda: self._show_results(results))

            # Git sync -- save clipboard to disk and push memory files
            if git:
                from memory.git_sync import save_clipboard, sync
                save_clipboard(self.orchestrator.clipboard)
                ok, msg = sync(f"MAGI session [{text[:40]}]")
                self.after(0, lambda m=msg: self.terminal_panel.append_text(
                    "SYSTEM", f"[GIT] {m}"
                ))
        except Exception as e:
            self.after(0, lambda: self.terminal_panel.append_text("SYSTEM", f"ERROR: {e}"))
        finally:
            loop.close()
            self.after(0, self._clear_thinking)
            self.after(0, lambda: self.vacant_panel.send_btn.configure(state="normal"))

    def _show_results(self, results: dict):
        tts_on = self.magi_panel.controls.voice_var.get()

        # MAGI core direct response (router handled it — no council needed)
        if "MAGI" in results:
            reply = results["MAGI"].strip()
            if reply:
                self.terminal_panel.append_text("MAGI", reply)
                if tts_on:
                    threading.Thread(target=self._speak, args=("MELCHIOR", reply), daemon=True).start()
            return

        for ai in ["MELCHIOR", "BALTHASAR", "CASPER"]:
            reply = results.get(ai, "").strip()
            if not reply or reply.startswith("[ERROR"):
                continue
            self.terminal_panel.append_text(ai, reply)
            if tts_on:
                threading.Thread(target=self._speak, args=(ai, reply), daemon=True).start()
        final = results.get("FINAL_DECISION", "").strip()
        if final and not final.startswith("[ERROR"):
            self.terminal_panel.append_text("MELCHIOR", f"[ SYNTHESIS ]\n{final}")
            if tts_on:
                threading.Thread(target=self._speak, args=("MELCHIOR", final), daemon=True).start()

        # Refinement output — shown separately, this is the print-ready version
        refined = results.get("REFINED", "").strip()
        if refined and not refined.startswith("[ERROR"):
            self.terminal_panel.append_text("SYSTEM", "◈ ─── REFINED OUTPUT ─── ◈")
            self.terminal_panel.append_text("MELCHIOR", f"[ REFINED ]\n{refined}")
            if tts_on:
                threading.Thread(target=self._speak, args=("MELCHIOR", refined), daemon=True).start()

        # Track last response for /memory command
        self._last_response = refined or final or ""

    def _commit_memory(self, note: str = ""):
        """Write last MAGI response to memory/pinned.md with timestamp."""
        import os
        from datetime import datetime
        if not self._last_response:
            self.terminal_panel.append_text("SYSTEM", "[/memory] Nothing to commit — no response yet.")
            return
        pinned_path = os.path.join(os.path.dirname(__file__), "..", "memory", "pinned.md")
        pinned_path = os.path.normpath(pinned_path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"### {timestamp}"
        if note:
            header += f" — {note}"
        entry = f"\n{header}\n\n{self._last_response}\n\n---\n"
        try:
            with open(pinned_path, "a", encoding="utf-8") as f:
                f.write(entry)
            self.terminal_panel.append_text("SYSTEM", f"[/memory] ✓ Committed to memory/pinned.md")
        except Exception as e:
            self.terminal_panel.append_text("SYSTEM", f"[/memory] ERROR: {e}")

    def _speak(self, ai: str, text: str):
        from voice.output import speak
        widget = getattr(self.magi_panel, ai.lower(), None)
        if widget:
            self.after(0, lambda w=widget: w.set_state("speaking"))
        voice = CONFIG.get(f"{ai}_VOICE", "Hugo")
        speak(text, voice)
        if widget:
            self.after(0, lambda w=widget: w.set_state("idle"))

    def run(self):
        self.mainloop()
