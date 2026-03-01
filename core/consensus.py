import difflib
from core.config import CONFIG


def calculate_similarity(text1: str, text2: str) -> float:
    """Returns a similarity ratio between 0 and 1."""
    t1 = text1.lower().strip()
    t2 = text2.lower().strip()
    return difflib.SequenceMatcher(None, t1, t2).ratio()


def check_agreement(responses: list) -> bool:
    """
    Returns True only if a meaningful majority consensus exists.
    Rules:
    - Any empty/error response = no consensus (debate must continue)
    - All responses must be non-trivially similar (≥ threshold)
    """
    if not responses or len(responses) < 2:
        return True

    # Empty or error responses are NOT consensus — debate must continue
    for r in responses:
        stripped = r.strip()
        if not stripped or stripped.startswith("[ERROR") or stripped.startswith("[TOOL"):
            return False

    threshold = CONFIG.get("CONSENSUS_THRESHOLD", 0.8)

    # All pairs must agree for true consensus (not just one pair)
    for i in range(len(responses)):
        for j in range(i + 1, len(responses)):
            if calculate_similarity(responses[i], responses[j]) < threshold:
                return False

    return True
