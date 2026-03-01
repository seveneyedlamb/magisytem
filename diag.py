import asyncio, sys, json, urllib.request
sys.path.insert(0, '.')

# Get model context_window from LM Studio
req = urllib.request.Request('http://localhost:1234/v1/models', headers={'Accept':'application/json'})
with urllib.request.urlopen(req, timeout=5) as r:
    raw = r.read().decode()

data = json.loads(raw)
for m in data.get('data', []):
    print("MODEL FIELDS:")
    for k, v in m.items():
        print(f"  {k} = {repr(v)[:200]}")

print()

# Check exact payload sizes
from core.personalities import MELCHIOR_PROMPT
from tools.schema import TOOL_SCHEMAS
import json as _json

schema_str = _json.dumps(TOOL_SCHEMAS)
print(f"MELCHIOR_PROMPT tokens (est): {len(MELCHIOR_PROMPT)//4}")
print(f"TOOL_SCHEMAS tokens (est):    {len(schema_str)//4}")
print(f"TOTAL before user msg:        {(len(MELCHIOR_PROMPT)+len(schema_str))//4}")
print()

from llm.client import make_api_call

async def run():
    user = "write a short article about war"
    
    # Test WITHOUT tools
    print("--- TEST: no tools ---")
    r = await make_api_call(MELCHIOR_PROMPT, [{"role":"user","content":user}])
    if "error" in r:
        print("FAIL:", r["error"][:200])
    else:
        u = r.get("usage", {})
        print(f"PASS: prompt={u.get('prompt_tokens')} completion={u.get('completion_tokens')}")
    
    # Test WITH tools
    print("--- TEST: with tools ---")
    r2 = await make_api_call(MELCHIOR_PROMPT, [{"role":"user","content":user}], tools=TOOL_SCHEMAS)
    if "error" in r2:
        print("FAIL:", r2["error"][:200])
    else:
        u2 = r2.get("usage", {})
        print(f"PASS: prompt={u2.get('prompt_tokens')} completion={u2.get('completion_tokens')}")

asyncio.run(run())
print("DONE")
