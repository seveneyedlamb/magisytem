try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

from core.config import CONFIG

def search_web(query: str, max_results: int = None) -> list[dict]:
    """
    Searches the web using DuckDuckGo.
    Returns a list of dicts with 'title', 'href', and 'body'.
    """
    if not CONFIG.get("WEB_SEARCH_ENABLED", True):
        return [{"error": "Web search is disabled in config."}]
        
    if DDGS is None:
        return [{"error": "duckduckgo-search package not installed."}]
        
    limit = min(max_results or CONFIG.get("MAX_SEARCH_RESULTS", 3), 3)
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=limit))
            return results
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]
