"""
Message history management for MAGI agents.
Keeps history construction out of client.py and orchestrator.py.
"""

def build_messages(system_prompt: str, history: list) -> list:
    """Prepend system prompt to the agent's conversation history."""
    return [{"role": "system", "content": system_prompt}] + history

def append_user(history: list, content: str) -> None:
    history.append({"role": "user", "content": content})

def append_assistant(history: list, content: str) -> None:
    history.append({"role": "assistant", "content": content})

def append_tool(history: list, tool_call_id: str, name: str, content: str) -> None:
    history.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": name,
        "content": content
    })
