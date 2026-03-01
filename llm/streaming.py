"""
SSE stream parser for LM Studio streaming responses.
Parse streaming chunks and yield content tokens.
"""

def parse_stream(response_lines) -> str:
    """
    Accepts an iterable of SSE lines from aiohttp streaming.
    Yields each content token string as it arrives.
    Usage: async for chunk in response.content: parse_stream(chunk)
    """
    import json

    for line in response_lines:
        line = line.strip()
        if not line or line == b"data: [DONE]" or line == "data: [DONE]":
            continue

        if isinstance(line, bytes):
            line = line.decode("utf-8")

        if line.startswith("data: "):
            raw = line[6:]
            try:
                data = json.loads(raw)
                delta = data.get("choices", [{}])[0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    yield token
            except json.JSONDecodeError:
                continue
