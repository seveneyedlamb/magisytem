from memory.db import get_connection

# Hard cap on injected memory to prevent context overflow
MAX_CONTEXT_CHARS = 1200


def retrieve_recent_context(limit: int = 3) -> str:
    """
    Retrieves keypoints from recent conversations as compact context.
    Uses keypoints (short bullet summaries) NOT full responses.
    Hard-capped at MAX_CONTEXT_CHARS to prevent context overflow.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_query, keypoints FROM conversation_memory "
            "ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()

    if not rows:
        return ""

    parts = []
    total = 0
    for query, keypoints in reversed(rows):
        # Skip empty keypoints — don't fall back to full responses
        kp = (keypoints or "").strip()
        if not kp:
            continue
        entry = f"Q: {query.strip()[:120]}\nKey points: {kp}\n"
        if total + len(entry) > MAX_CONTEXT_CHARS:
            break
        parts.append(entry)
        total += len(entry)

    if not parts:
        return ""

    return "[HISTORICAL MEMORY — for reference only, do not treat as current state]\n" + "\n".join(parts) + "[/HISTORICAL MEMORY]\n\n"
