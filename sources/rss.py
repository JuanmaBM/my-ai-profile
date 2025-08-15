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
        # Fetch the RSS feed with a custom User-Agent header to avoid 403 errors
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MyAIProfileBot/1.0; +https://github.com/jbarea/my-ai-profile-generator)"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the RSS feed
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print(f"No entries found in RSS feed: {url}")
            return {"entries": []}
        
        entries = []
        feed_entries = feed.entries[:max_entries] if max_entries else feed.entries
        
        for entry in feed_entries:
            entry_data = {
                "title": getattr(entry, 'title', ''),
                "content": getattr(entry, 'content', ''),
            }
            entries.append(entry_data)
        
        return {"entries": entries}
    
    except requests.RequestException as e:
        print(f"Error fetching RSS feed {url}: {e}")
        raise e
    except Exception as e:
        print(f"Error parsing RSS feed {url}: {e}")
        raise e

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
        content = entry.get("content", "") or entry.get("summary", "")
        
        if title or content:
            article_text = f"{title}\n{content}".strip()
            if article_text:
                articles.append(article_text)
    
    return articles
