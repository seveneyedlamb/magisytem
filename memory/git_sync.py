"""
memory/git_sync.py

Syncs memory files to the configured git remote.
Called when Git Mode is enabled after each deliberation.

What gets synced:
  - memory/pinned.md    (pinned conversations)
  - memory/clipboard.json  (session clipboard items)

On a new machine: git pull, then MAGI loads clipboard.json on startup.
"""
import json
import subprocess
import os
from datetime import datetime

# Path to the memory directory (relative to repo root)
_MEMORY_DIR = os.path.join(os.path.dirname(__file__))
_REPO_ROOT = os.path.dirname(_MEMORY_DIR)

CLIPBOARD_PATH = os.path.join(_MEMORY_DIR, "clipboard.json")
PINNED_PATH = os.path.join(_MEMORY_DIR, "pinned.md")


def _run(cmd: list[str]) -> tuple[bool, str]:
    """Run a git command in the repo root. Returns (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "git command timed out"
    except Exception as e:
        return False, str(e)


def save_clipboard(clipboard: list[str]) -> None:
    """Persist clipboard to disk so it can be committed and pulled on other machines."""
    try:
        with open(CLIPBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump({"items": clipboard, "updated": datetime.now().isoformat()}, f, indent=2)
    except Exception:
        pass


def load_clipboard() -> list[str]:
    """Load clipboard from disk on startup (enables cross-machine continuity)."""
    try:
        if os.path.exists(CLIPBOARD_PATH):
            with open(CLIPBOARD_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("items", [])
    except Exception:
        pass
    return []


def pull() -> tuple[bool, str]:
    """Pull latest changes from remote (call on startup in git mode)."""
    return _run(["git", "pull", "--rebase", "origin"])


def sync(commit_message: str = None) -> tuple[bool, str]:
    """
    Stage memory files, commit, and push.
    Returns (success, status_message).
    """
    if not commit_message:
        commit_message = f"MAGI memory sync [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"

    # Stage only memory files -- never the whole repo
    files_to_stage = []
    for path in [CLIPBOARD_PATH, PINNED_PATH]:
        if os.path.exists(path):
            files_to_stage.append(path)

    if not files_to_stage:
        return True, "Nothing to sync."

    ok, out = _run(["git", "add"] + files_to_stage)
    if not ok:
        return False, f"git add failed: {out}"

    # Check if there's actually anything to commit
    check_ok, check_out = _run(["git", "diff", "--cached", "--quiet"])
    if check_ok:  # exit 0 = nothing staged
        return True, "Memory unchanged -- nothing to push."

    ok, out = _run(["git", "commit", "-m", commit_message])
    if not ok:
        return False, f"git commit failed: {out}"

    ok, out = _run(["git", "push", "origin"])
    if not ok:
        return False, f"git push failed: {out}"

    return True, f"Synced to git: {commit_message}"
