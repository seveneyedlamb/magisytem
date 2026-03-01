from memory.db import get_connection

def store_conversation(query: str, responses: dict, keypoints: str = ""):
    """
    Stores a deliberation cycle into the database.
    responses is a dict mapping AI names to their final text.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_memory (
                user_query, melchior_response, balthasar_response, 
                casper_response, final_decision, keypoints
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            query,
            responses.get("MELCHIOR", ""),
            responses.get("BALTHASAR", ""),
            responses.get("CASPER", ""),
            responses.get("FINAL_DECISION", ""),
            keypoints
        ))
        conn.commit()
    return True
