import os
from typing import List, Optional, Any
from urllib.parse import urlparse

try:
    from linkedin_api import Linkedin  # type: ignore
except Exception:  # pragma: no cover
    Linkedin = None  # Fallback if the package is not available at runtime


def _ensure_linkedin_client() -> Optional["Linkedin"]:
    """Create a Linkedin API client using env vars.
    """
    if Linkedin is None:
        return None

    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        return None
    try:
        return Linkedin(email, password)
    except Exception:
        return None


def _collect_text_fields(obj: Any, results: List[str]) -> None:
    """Recursively collect likely human-readable text fields from a nested dict/list structure."""
    if obj is None:
        return
    if isinstance(obj, str):
        stripped = obj.strip()
        if stripped:
            results.append(stripped)
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Prefer common content-bearing keys
            if key in {"text", "title", "description", "commentary"}:
                _collect_text_fields(value, results)
            else:
                _collect_text_fields(value, results)
        return
    if isinstance(obj, list):
        for item in obj:
            _collect_text_fields(item, results)
        return


def _extract_post_text(post: dict) -> Optional[str]:
    """Extract the main post text from a LinkedIn update payload.

    Strategy:
    1) Try known structured paths first (commentary/message/shareCommentary)
    2) Clean URLs and noise
    3) Fallback: collect all text-like fields, filter out URLs/URNs/constants, pick longest meaningful
    """
    import re
    from typing import Any as _Any, List as _List, Optional as _Optional

    def _deep_get(d: _Any, path: _List[str]) -> _Optional[_Any]:
        cur: _Any = d
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
        return cur

    def _normalize_text(value: _Any) -> _Optional[str]:
        # Handle nested {"text": "..."}
        if isinstance(value, dict) and "text" in value and isinstance(value["text"], str):
            value = value["text"]
        if not isinstance(value, str):
            return None
        text = value.strip()
        # Strip URLs
        text = re.sub(r"https?://\S+", "", text).strip()
        # Collapse excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text if text else None

    structured_paths: _List[_List[str]] = [
        ["commentary", "text", "text"],
        ["commentary", "text"],
        ["updateMetadata", "commentary", "text", "text"],
        ["updateMetadata", "commentary", "text"],
        ["value", "com.linkedin.voyager.feed.render.UpdateV2", "updateMetadata", "commentary", "text", "text"],
        ["value", "com.linkedin.voyager.feed.render.UpdateV2", "commentary", "text", "text"],
        ["value", "com.linkedin.voyager.feed.render.UpdateV2", "message", "text"],
        ["specificContent", "com.linkedin.ugc.ShareContent", "shareCommentary", "text"],
    ]

    for path in structured_paths:
        raw = _deep_get(post, path)
        text = _normalize_text(raw)
        if text and len(text) >= 20:
            return text

    # Fallback: scan all text-like fields, filtering noise
    collected: _List[str] = []
    _collect_text_fields(post, collected)

    def _is_noise(s: str) -> bool:
        if not s or len(s) < 20:
            return True
        if s.startswith("http://") or s.startswith("https://"):
            return True
        if s.startswith("urn:"):
            return True
        if s.isupper() and any(c.isalpha() for c in s):
            return True  # UI constants like SYS_ICN_*
        if "/" in s and not any(ch.isspace() for ch in s):
            return True  # paths/tokens
        if not any(ch.isspace() for ch in s) and len(s) > 40:
            return True  # long hashes/tokens
        return False

    filtered = [re.sub(r"https?://\S+", "", s).strip() for s in collected if not _is_noise(s)]
    filtered = [re.sub(r"\s+", " ", s).strip() for s in filtered if s]

    if not filtered:
        return None

    # Prefer the longest meaningful chunk
    filtered.sort(key=len, reverse=True)
    return filtered[0]


def _coerce_posts(obj: Any) -> List[dict]:
    """Normalize API responses to a list of post dicts."""
    if obj is None:
        return []
    if isinstance(obj, list):
        return [p for p in obj if isinstance(p, dict)]
    if isinstance(obj, dict):
        # Common pattern: { 'elements': [ ... ] }
        elements = obj.get("elements")
        if isinstance(elements, list):
            return [p for p in elements if isinstance(p, dict)]
    return []


def _fetch_user_posts(api: "Linkedin", public_id: str) -> List[dict]:
    """Fetch posts/updates using several method names supported in different versions."""
    debug = os.getenv("LINKEDIN_DEBUG", "0") == "1"

    aggregated: List[dict] = []
    try:
        res = api.get_profile_updates(public_id, max_results=10)
        posts = _coerce_posts(res)
        if posts:
            aggregated.extend(posts)
    except Exception as e:
        if debug:
            print(f"[linkedin] call without pagination failed: {e}")

    return aggregated


def fetch_linkedin_articles(user: str) -> List[str]:
    """Fetch all available LinkedIn posts for a user and return a list of post contents.

    Authentication:
    - Either LINKEDIN_LI_AT (+ optional LINKEDIN_JSESSIONID) or LINKEDIN_EMAIL + LINKEDIN_PASSWORD

    Notes:
    - This uses the unofficial `linkedin-api` package and may be subject to breakage due to
      LinkedIn website changes or account restrictions such as 2FA/challenges.
    - The function returns only textual content extracted from posts, best-effort.
    """
    api = _ensure_linkedin_client()
    if api is None:
        return []

    contents: List[str] = []
    posts = _fetch_user_posts(api, user)
    if not posts:
        return []

    for post in posts:
        try:
            text = _extract_post_text(post)
            if text:
                contents.append(text)
        except Exception as e:
            print(f"[linkedin] error extracting post text: {e}")
            continue

    return contents
