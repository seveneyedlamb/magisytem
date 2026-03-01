import aiohttp
from core.config import CONFIG

# Qwen 3.5 is a reasoning model that generates 5000+ tokens by default.
# Three agents * 5000 tokens = 15k+ input to synthesis = context overflow.
# Cap at 1500 tokens per agent call to keep synthesis input manageable.
MAX_AGENT_TOKENS = CONFIG.get("MAX_AGENT_TOKENS", 1500)

async def make_api_call(system_prompt, messages, stream=False, tools=None, max_tokens=None):
    """
    Connects to the local LLM server (e.g., LM Studio) and makes an API call.
    Returns the parsed JSON response if stream=False, or an error dict.
    """
    url = f"{CONFIG.get('LM_STUDIO_URL', 'http://localhost:1234/v1')}/chat/completions"
    model = CONFIG.get('MODEL_NAME', 'qwen3.5-35b-a3b')

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": stream,
        "max_tokens": max_tokens or MAX_AGENT_TOKENS,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    return {"error": f"HTTP {response.status}: {text}"}
    except Exception as e:
        return {"error": str(e)}
