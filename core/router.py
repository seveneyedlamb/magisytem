"""
MAGI System Core — query triage router.
This is the 4th AI instance. It does not debate, it does not communicate.
It decides whether a query needs the full council (MELCHIOR, BALTHASAR, CASPER)
or can be handled as a direct simple response.
"""
import json
from llm.client import make_api_call

MAGI_ROUTER_PROMPT = """You are the MAGI System Core — a silent triage intelligence.

Your sole function: decide how to handle each incoming query.

ROUTE AS "simple" ONLY when the query is:
- Pure casual conversation or greetings ("hello", "thanks", "good morning")
- Trivially obvious facts that need no research ("what is 2+2")
- Short acknowledgements with no information need

ROUTE AS "deliberate" when the query involves ANY of the following:
- Questions about system capabilities ("can you...", "are you able to...", "do you have...")
- Requests to search, browse, look up, find, or research anything on the web
- Technical problems, analysis, or multi-step reasoning
- Complex decisions requiring multiple perspectives  
- Strategy, ethics, trade-offs, opinions
- ANYTHING where a wrong answer would be harmful

When in doubt, ALWAYS route as "deliberate". The council is cheap. False confidence is not.

Respond in valid JSON only. No extra text.

If simple:
{"mode": "simple", "reply": "<your direct, concise answer here>"}

If deliberate:
{"mode": "deliberate"}
"""


async def triage_query(question: str) -> dict:
    """
    Routes the query. Returns dict with 'mode' key:
    - {"mode": "simple", "reply": "..."} — answer directly
    - {"mode": "deliberate"}             — engage the council
    """
    messages = [{"role": "user", "content": question}]
    result = await make_api_call(MAGI_ROUTER_PROMPT, messages)

    if "error" in result:
        # On router failure, default to deliberation
        return {"mode": "deliberate"}

    content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

    # Strip markdown code fences if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        parsed = json.loads(content)
        if parsed.get("mode") in ("simple", "deliberate"):
            return parsed
    except Exception:
        pass

    # Fallback: if we can't parse JSON, deliberate
    return {"mode": "deliberate"}
