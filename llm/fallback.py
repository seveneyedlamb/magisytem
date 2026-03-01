"""
Claude API fallback for when LM Studio is unavailable.
Returns same response shape as llm/client.py make_api_call.
"""
import aiohttp
from core.config import CONFIG

async def make_claude_call(system_prompt: str, messages: list) -> dict:
    """
    Calls the Claude API as a fallback when local LM Studio is offline.
    Requires CLAUDE_API_KEY in config.txt.
    Returns same shape as make_api_call: {"choices": [{"message": {...}}]}
    """
    api_key = CONFIG.get("CLAUDE_API_KEY", "")
    if not api_key:
        return {"error": "No CLAUDE_API_KEY configured."}

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "system": system_prompt,
        "messages": messages,
        "max_tokens": 4096
    }

    try:
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Normalize to OpenAI shape
                    content = data.get("content", [{}])[0].get("text", "")
                    return {"choices": [{"message": {"role": "assistant", "content": content}}]}
                text = await resp.text()
                return {"error": f"Claude HTTP {resp.status}: {text}"}
    except Exception as e:
        return {"error": str(e)}
