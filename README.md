# MAGI System

> A multi-agent AI deliberation system powered by local LLMs via LM Studio.
> Three philosophical AI agents -- CASPER, BALTHASAR, and MELCHIOR -- debate, reason, and synthesize answers to complex questions.

## Architecture

- **CASPER** -- the creative wildcard. Speaks first. Finds angles no one else looks at.
- **BALTHASAR** -- the realist. Responds to CASPER. Questions assumptions. Names what might go wrong.
- **MELCHIOR** -- the coordinator. Reads both. Synthesizes or calls for more debate.
- **MAGI CORE** -- the overseer. Reformulates raw queries into structured council briefings.

## Features

- Sequential philosophical dialogue (not parallel echo-chamber)
- Debate Mode toggle -- full council OR fast MELCHIOR-direct answers
- Session Clipboard -- agents flag important facts, MAGI Core evaluates, council can override
- Research pipeline -- one focused search pass before deliberation
- `/memory` command -- pin important responses to `memory/pinned.md`
- Refinement Mode -- second-pass polish via Dave Barry-style synthesis
- Git Mode -- auto-sync memory and clipboard to GitHub for cross-machine continuity
- Voice output support
- Customizable context files (`.md`/`.txt`)

## Requirements

- Python 3.11+
- [LM Studio](https://lmstudio.ai/) running locally with a model loaded
- `pip install -r requirements.txt` (customtkinter, aiohttp, duckduckgo-search)

## Setup

```bash
git clone https://github.com/seveneyedlamb/magisytem.git
cd magisytem
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install customtkinter aiohttp duckduckgo-search
python main.py
```

Set your LM Studio URL and model in `config.txt`.

## Git Mode (Cross-Machine Memory)

Enable the **Git** toggle in the context bar. After each session, MAGI will commit
and push `memory/pinned.md` and `memory/clipboard.json` to your fork of this repo.
On a new machine, just pull and your memory syncs automatically.

## License

MIT -- free to use, fork, and build on.
