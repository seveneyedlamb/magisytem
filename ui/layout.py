"""
Grid layout configuration for MAGI application.
Grid setup only — no widget creation.
"""

def apply_layout(app, magi_panel, terminal_panel, context_bar, vacant_panel) -> None:
    """Configure the 60/40 split grid and place all panels."""
    app.grid_rowconfigure(0, weight=1)
    app.grid_rowconfigure(1, weight=0)  # context bar
    app.grid_rowconfigure(2, weight=0)  # input area
    app.grid_columnconfigure(0, weight=0, minsize=720)
    app.grid_columnconfigure(1, weight=0, minsize=480)

    magi_panel.grid(row=0, column=0, rowspan=3, sticky="nsew")
    terminal_panel.grid(row=0, column=1, sticky="nsew")
    context_bar.grid(row=1, column=1, sticky="ew")
    vacant_panel.grid(row=2, column=1, sticky="nsew")
