import sys
import os
import asyncio

# Ensure core and llm modules are importable
sys.path.insert(0, os.path.abspath('.'))

from llm.client import make_api_call
from core.personalities import MELCHIOR_PROMPT, BALTHASAR_PROMPT, CASPER_PROMPT

async def text_single_personality():
    print("--- Step 3: Testing single personality (MELCHIOR) ---")
    messages = [{"role": "user", "content": "What is 2+2? Reply briefly."}]
    result = await make_api_call(MELCHIOR_PROMPT, messages, stream=False)
    
    if "error" in result:
        print(f"LM Studio not reachable: {result['error']}")
    else:
        choice = result.get('choices', [{}])[0]
        content = choice.get('message', {}).get('content', '')
        print(f"MELCHIOR: {content}")

async def test_parallel_calls():
    print("\n--- Step 4: Testing three parallel calls ---")
    question = "Is the sky blue? Answer with 'Yes' or 'No' and one sentence why."
    messages = [{"role": "user", "content": question}]
    
    print("Initiating parallel calls to Melchior, Balthasar, and Casper...")
    results = await asyncio.gather(
        make_api_call(MELCHIOR_PROMPT, messages, stream=False),
        make_api_call(BALTHASAR_PROMPT, messages, stream=False),
        make_api_call(CASPER_PROMPT, messages, stream=False)
    )
    
    names = ["MELCHIOR", "BALTHASAR", "CASPER"]
    for name, result in zip(names, results):
        if "error" in result:
             print(f"{name} Error: {result['error']}")
        else:
             content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
             print(f"{name}: {content}")

async def main():
    await text_single_personality()
    await test_parallel_calls()

if __name__ == "__main__":
    asyncio.run(main())
