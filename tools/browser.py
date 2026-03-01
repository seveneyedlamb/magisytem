"""
Web reader tool using Jina AI Reader API.
Standard AI agent pattern — single HTTP GET to r.jina.ai/{url}
Returns clean LLM-ready markdown. No browser, no dependencies.
Also provides Jina Search (s.jina.ai) for Google-style search with full content.
"""
import urllib.request
import urllib.parse

MAX_CONTENT_CHARS = 1200

JINA_HEADERS = {
    "Accept": "text/plain",
    "User-Agent": "MAGI-System/1.0",
    "X-Return-Format": "markdown",
}


def read_url(url: str) -> str:
    """
    Fetches a URL through Jina AI Reader and returns clean markdown content.
    Works on JS-heavy pages, news sites, docs — anything with real content.
    """
    try:
        jina_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(jina_url, headers=JINA_HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        if len(content) > MAX_CONTENT_CHARS:
            content = content[:MAX_CONTENT_CHARS] + "\n[Content truncated]"
        return content
    except Exception as e:
        return f"[ERROR reading {url}: {e}]"


def jina_search(query: str) -> str:
    """
    Searches the web via Jina AI Search (s.jina.ai) — returns clean results
    with titles, URLs, and full page summaries. Better than raw DuckDuckGo
    for finding and reading information in one step.
    """
    try:
        encoded = urllib.parse.quote(query)
        jina_url = f"https://s.jina.ai/{encoded}"
        req = urllib.request.Request(jina_url, headers=JINA_HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        if len(content) > MAX_CONTENT_CHARS:
            content = content[:MAX_CONTENT_CHARS] + "\n[Results truncated]"
        return content
    except Exception as e:
        return f"[ERROR searching '{query}': {e}]"
