import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from core.orchestrator import MAGIOrchestrator

async def run_amendment_test():
    print("--- Testing Phase 7 Amendments ---")
    orchestrator = MAGIOrchestrator()
    
    def log_status(msg):
        print(f"[STATUS] {msg}")
        
    print("\n[TEST] 1: Submitting a query that requires Web Search and Keypoint Extraction")
    # This invokes all the amended flows at once
    res = await orchestrator.process_query(
        "Based on recent news, what Company does Tim Cook lead?", 
        address_mode="MELCHIOR", 
        status_callback=log_status
    )
    
    print("\n[RESULTS]")
    print(res.get("MELCHIOR", "No response from Melchior"))
    print("\n[TEST] Script completed gracefully. Check data/magi.db manually for the populated keypoints.")

if __name__ == "__main__":
    asyncio.run(run_amendment_test())
