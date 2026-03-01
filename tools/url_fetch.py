import urllib.request
from bs4 import BeautifulSoup
import re

def fetch_url_content(url: str, max_chars=5000) -> str:
    """
    Fetches the content of a URL and extracts the readable text.
    Strips raw HTML and returns plain text up to max_chars.
    """
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > max_chars:
            text = text[:max_chars] + "... [TRUNCATED]"
            
        return text
    except Exception as e:
        return f"[ERROR FETCHING URL: {str(e)}]"
