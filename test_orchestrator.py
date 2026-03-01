import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath('.'))

from core.orchestrator import MAGIOrchestrator

def print_status(msg):
    print(f"[MAGI STATUS] {msg}")

async def test_orchestrator():
    print("--- Testing Phase 2 Core Logic (Orchestrator, Debate, Addressing) ---")
    orchestrator = MAGIOrchestrator()
    
    # 1. Test single-AI addressing
    print("\n[TEST 1] Testing single-AI addressing mode (CASPER)...")
    res = await orchestrator.process_query("Tell me a completely unbelievable lie.", address_mode="CASPER", status_callback=print_status)
    print(f"CASPER final: {res.get('CASPER')[:100]}...")
    
    # 2. Test full orchestrator flow (with dummy responses due to connection logic)
    print("\n[TEST 2] Testing full orchestrator flow (ALL mode)...")
    orchestrator.reset_history()
    # If LM Studio is not running, strings will be error messages. 
    # Check_agreement should agree on errors because they are identical strings or very similar, bypassing debate round 2 unless forced.
    # We will trigger it anyway to see the loops.
    
    res = await orchestrator.process_query("What is the best programming language?", address_mode="ALL", status_callback=print_status)
    print("Synthesis complete! Final JSON structure contains:")
    for k in res.keys():
        print(f"  - {k}")
    
    print("\nOrchestrator structure works successfully if we reached this point without crashing.")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
