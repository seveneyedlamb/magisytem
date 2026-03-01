import sys
import os
import asyncio

# Ensure project modules are importable
sys.path.insert(0, os.path.abspath('.'))

from llm.client import make_api_call

async def main():
    print("Testing LLM connection...")
    system_prompt = "You are a helpful assistant serving as a connection test."
    messages = [{"role": "user", "content": "Just reply with exactly 'Connection successful!'"}]
    
    result = await make_api_call(system_prompt, messages, stream=False)
    
    if "error" in result:
        print(f"Connection test failed or LM Studio is not running: {result['error']}")
    else:
        # Extract response text based on standard OpenAI JSON format
        choice = result.get('choices', [{}])[0]
        content = choice.get('message', {}).get('content', '')
        print("Raw response:")
        print(result)
        print("\nExtracted message:")
        print(content)

if __name__ == "__main__":
    asyncio.run(main())
