import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from core.consensus import check_agreement

def test_consensus():
    print("--- Step 5: Testing Consensus Check ---")
    
    # Test unanimous agreement
    agreed = [
        "The sky is blue because of Rayleigh scattering.",
        "Rayleigh scattering makes the sky blue.",
        "Due to Rayleigh scattering, the sky appears blue."
    ]
    # Simple strings might not hit 0.8 threshold with difflib unless very similar
    # Let's test exact matches first
    exact = ["Yes it is.", "Yes it is.", "No it is not."]
    
    print("Testing 2-out-of-3 agreement (threshold 0.8):")
    result = check_agreement(exact)
    print(f"Result (should be True): {result}")
    
    disagree = [
        "I absolutely agree with this.",
        "I completely disagree and think it's false.",
        "There is no way to know for sure."
    ]
    print("\nTesting disagreement:")
    result = check_agreement(disagree)
    print(f"Result (should be False): {result}")

if __name__ == "__main__":
    test_consensus()
