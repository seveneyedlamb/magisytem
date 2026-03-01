from llm.client import make_api_call
import asyncio

async def extract_keypoints(query: str, final_decision: str) -> str:
    """
    Uses the LLM to extract a brief summary or key points from a conversation.
    This saves space in the SQLite database compared to full text.
    """
    system_prompt = "You are a summarizing subroutine. Extract 1-3 bullet points representing the core decision or key facts from the provided interaction. Be extremely concise. Output nothing else."
    
    content = f"User Query: {query}\n\nFinal Decision: {final_decision}"
    messages = [{"role": "user", "content": content}]
    
    result = await make_api_call(system_prompt, messages, stream=False)
    
    if "error" in result:
        return "[Error extracting keypoints]"
        
    reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
    return reply.strip()
