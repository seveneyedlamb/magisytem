import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from tools.web_search import search_web
from tools.url_fetch import fetch_url_content

def test_tools():
    print("--- Testing Phase 6 Tools ---")
    
    print("\n[TEST 1] Web Search (DuckDuckGo)")
    res = search_web("Magi supercomputer Evangelion", max_results=1)
    if res and len(res) > 0:
        print(f"Title: {res[0].get('title', 'N/A')}")
        print(f"Body snippet: {res[0].get('body', 'N/A')[:100]}...")
    else:
        print("Search failed or returned no results. Check internet connection/dependencies.")
        
    print("\n[TEST 2] URL Fetch (BeautifulSoup)")
    text = fetch_url_content("https://en.wikipedia.org/wiki/Neon_Genesis_Evangelion", max_chars=200)
    print(f"Extracted Text:\n{text}")

if __name__ == "__main__":
    test_tools()
