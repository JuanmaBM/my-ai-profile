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
        # Try multiple User-Agent strategies to avoid 403 errors
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "feedparser/6.0.10",
            "Mozilla/5.0 (compatible; RSS Reader)"
        ]
        
        response = None
        last_error = None
        
        for user_agent in user_agents:
            try:
                headers = {
                    "User-Agent": user_agent,
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
                response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
                response.raise_for_status()
                break  # If successful, break out of the loop
            except requests.exceptions.HTTPError as e:
                last_error = e
                if response and response.status_code == 403:
                    print(f"403 error with User-Agent: {user_agent}")
                    continue  # Try next user agent
                else:
                    raise e  # If it's not a 403, raise immediately
            except Exception as e:
                last_error = e
                continue  # Try next user agent
        
        if response is None or response.status_code != 200:
            raise last_error or Exception("All User-Agent attempts failed")
        
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
        return {"entries": []}
    except Exception as e:
        print(f"Error parsing RSS feed {url}: {e}")
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
        content = entry.get("content", "") or entry.get("summary", "")
        
        if title or content:
            article_text = f"{title}\n{content}".strip()
            if article_text:
                articles.append(article_text)
    
    return articles
