"""
Indicator animation effects — glow/pulse for active state.
Uses CTk's after() loop for non-blocking animation.
"""

_pulse_jobs = {}

def pulse_indicator(indicator_widget, color: str, interval_ms: int = 600) -> None:
    """Start a pulse animation on an indicator widget by alternating active/dim states."""
    _pulse_step(indicator_widget, color, bright=True, interval_ms=interval_ms)

def _pulse_step(widget, color: str, bright: bool, interval_ms: int) -> None:
    if widget not in _pulse_jobs:
        return  # Animation was cancelled

    if bright:
        widget.configure(fg_color=color)
    else:
        widget.configure(fg_color=_dim(color))

    job = widget.after(interval_ms, lambda: _pulse_step(widget, color, not bright, interval_ms))
    _pulse_jobs[widget] = job

def start_pulse(indicator_widget, color: str) -> None:
    """Register and start the pulse effect."""
    _pulse_jobs[indicator_widget] = True
    pulse_indicator(indicator_widget, color)

def stop_pulse(indicator_widget) -> None:
    """Cancel the pulse animation and return to dim idle state."""
    job = _pulse_jobs.pop(indicator_widget, None)
    if job and job is not True:
        try:
            indicator_widget.after_cancel(job)
        except Exception:
            pass

def _dim(hex_color: str) -> str:
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"#{int(r*0.25):02x}{int(g*0.25):02x}{int(b*0.25):02x}"
