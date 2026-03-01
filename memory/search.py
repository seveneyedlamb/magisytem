from memory.db import get_connection

def search_memory(keyword: str, limit=5) -> list:
    """
    Performs a basic text search against past conversations.
    Returns a list of dicts with timestamp, query, and decision.
    """
    results = []
    with get_connection() as conn:
        cursor = conn.cursor()
        search_pattern = f"%{keyword}%"
        cursor.execute('''
            SELECT timestamp, user_query, final_decision 
            FROM conversation_memory 
            WHERE user_query LIKE ? OR final_decision LIKE ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (search_pattern, search_pattern, limit))
        
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "query": row[1],
                "decision": row[2]
            })
            
    return results
