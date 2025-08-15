import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import re


def fetch_rss_content(url: str, max_entries: Optional[int] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Fetch and parse RSS feed content from the given URL.
    
    Args:
        url (str): RSS feed URL to fetch
        max_entries (Optional[int]): Maximum number of entries to return (None for all)
    
    Returns:
        Dict containing 'entries' list with title, link, summary, content, and published_date
    """
    try:
        print(f"Fetching RSS feed: {url}")
        
        # Simple approach: just use feedparser with a good User-Agent
        feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        feed = feedparser.parse(url)
        
        if not feed.entries:
            print(f"No entries found in RSS feed: {url}")
            return {"entries": []}
        
        entries = []
        feed_entries = feed.entries[:max_entries] if max_entries else feed.entries
        
        for entry in feed_entries:
            # Extract entry data
            entry_data = {
                "title": getattr(entry, 'title', ''),
                "content": getattr(entry, 'content', ''),
            }
            entries.append(entry_data)
        
        return {"entries": entries}
    
    except Exception as e:
        print(f"Error processing RSS feed {url}: {e}")
        return {"entries": []}


def get_rss_articles_text(url: str, max_entries: Optional[int] = None) -> List[str]:
    """
    Fetch RSS feed and return a list of article texts (combining title and content).
    
    Args:
        url (str): RSS feed URL to fetch
        max_entries (Optional[int]): Maximum number of entries to return
    
    Returns:
        List of strings containing article texts
    """
    rss_data = fetch_rss_content(url, max_entries)
    articles = []
    
    for entry in rss_data.get("entries", []):
        # Combine title and content for analysis
        title = entry.get("title", "")
        content = entry.get("content", "")
        
        # Handle content that might be a list (from feedparser)
        if isinstance(content, list) and content:
            content = content[0].get('value', '') if isinstance(content[0], dict) else str(content[0])
        elif hasattr(content, 'value'):
            content = content.value
        elif not isinstance(content, str):
            content = str(content)
        
        # Clean HTML tags if present
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        if title or content:
            article_text = f"{title}\n{content}".strip()
            if article_text:
                articles.append(article_text)
    
    return articles
