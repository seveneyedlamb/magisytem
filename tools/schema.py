# Tool JSON schemas for LM Studio API.
# Single source of truth — imported by orchestrator.

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web using DuckDuckGo. Returns titles, URLs, and snippets. Use for quick lookups.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Max results (default 5)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jina_search",
            "description": (
                "Searches the web via Jina AI and returns full page content for each result — "
                "titles, URLs, and readable summaries. Better than search_web when you need "
                "to actually read the content, not just get links. Use for research tasks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to research"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": (
                "Reads a URL and returns its content as clean markdown text via Jina AI Reader. "
                "Works on news articles, documentation, blogs, and most web pages. "
                "Use when you have a specific URL to read."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL to read"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url_content",
            "description": "Fast HTTP fetch for simple static pages. Fallback if read_url fails.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to fetch"}
                },
                "required": ["url"]
            }
        }
    }
]
