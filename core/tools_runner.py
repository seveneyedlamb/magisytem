import json
from tools.web_search import search_web
from tools.url_fetch import fetch_url_content
from tools.browser import read_url, jina_search


def execute_tool(name: str, kwargs: dict) -> str:
    """
    Executes the named tool with the provided kwargs.
    Returns the result as a string for injection into message history.
    """
    if name == "search_web":
        results = search_web(**kwargs)
        return json.dumps(results)

    if name == "jina_search":
        return jina_search(**kwargs)

    if name == "read_url":
        return read_url(**kwargs)

    if name == "fetch_url_content":
        return fetch_url_content(**kwargs)

    return f"[ERROR: Unknown tool '{name}']"
