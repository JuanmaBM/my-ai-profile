from llm.llm_client import analyze
import os
import re
import requests
from urllib.parse import urlparse
from typing import List, Dict, Tuple, Optional


_GITHUB_API = "https://api.github.com"
_RAW_BASE = "https://raw.githubusercontent.com"
_EXT_TO_LANGUAGE: Dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".rs": "Rust",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".dart": "Dart",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".R": "R",
    ".jl": "Julia",
    ".hs": "Haskell",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".md": "Markdown",
    "Dockerfile": "Dockerfile",
}


def _github_headers() -> Dict[str, str]:
    """Build headers with optional token for higher rate limits."""
    headers: Dict[str, str] = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _parse_repo_link(repo_link: str) -> Optional[Tuple[str, str]]:
    """Parse a GitHub repo URL like https://github.com/{owner}/{repo}."""
    try:
        parsed = urlparse(repo_link)
        if parsed.netloc not in {"github.com", "www.github.com"}:
            return None
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) < 2:
            return None
        owner, repo = parts[0], parts[1].replace(".git", "")
        return owner, repo
    except Exception as e:
        print(f"[github] error parsing repo link '{repo_link}': {e}")
        return None


def _fetch_repo_info(owner: str, repo: str) -> Optional[Dict]:
    """Fetch repo metadata to get default branch and other info."""
    url = f"{_GITHUB_API}/repos/{owner}/{repo}"
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    if resp.status_code != 200:
        return None
    return resp.json()


def _fetch_languages(owner: str, repo: str) -> Dict[str, int]:
    """Fetch language usage (bytes per language)."""
    url = f"{_GITHUB_API}/repos/{owner}/{repo}/languages"
    resp = requests.get(url, headers=_github_headers(), timeout=15)
    if resp.status_code != 200:
        return {}
    return resp.json() or {}


def _list_repo_paths(owner: str, repo: str, ref: str, path: str = "") -> List[Dict]:
    """List files and directories via Contents API for a given path."""
    api_path = path.strip("/")
    url = f"{_GITHUB_API}/repos/{owner}/{repo}/contents/{api_path}"
    params = {"ref": ref} if ref else None
    resp = requests.get(url, headers=_github_headers(), params=params, timeout=15)
    if resp.status_code != 200:
        return []
    data = resp.json()
    if isinstance(data, dict):
        return [data]
    return data or []


def _detect_language_by_path(path: str) -> Optional[str]:
    """Infer language from file extension or special filenames like Dockerfile."""
    basename = path.split("/")[-1]
    if basename == "Dockerfile":
        return "Dockerfile"
    match = re.search(r"(\.[A-Za-z0-9_]+)$", basename)
    if not match:
        return None
    ext = match.group(1)
    return _EXT_TO_LANGUAGE.get(ext)


def _fetch_raw_file(owner: str, repo: str, ref: str, path: str) -> Optional[str]:
    """Download raw file content for a given path at a ref (branch)."""
    path_no_slash = path.lstrip("/")
    url = f"{_RAW_BASE}/{owner}/{repo}/{ref}/{path_no_slash}"
    resp = requests.get(url, headers=_github_headers(), timeout=20)
    if resp.status_code != 200:
        return None
    return resp.text


def _collect_repo_samples(owner: str, repo: str, default_branch: str, max_files: int = 12, max_chars: int = 4000) -> Dict[str, List[Tuple[str, str]]]:
    """Collect small samples of files grouped by detected language.

    Returns a dict language -> list of (path, truncated_content).
    """
    grouped: Dict[str, List[Tuple[str, str]]] = {}
    seen = 0

    # Breadth-first traversal limited to common source directories
    candidate_dirs = ["", "src", "lib", "app", "backend", "frontend"]

    for base in candidate_dirs:
        if seen >= max_files:
            break
        items = _list_repo_paths(owner, repo, default_branch, base)
        for item in items:
            if seen >= max_files:
                break
            if item.get("type") == "file":
                path = item.get("path", "")
                language = _detect_language_by_path(path)
                if not language:
                    continue
                content = _fetch_raw_file(owner, repo, default_branch, path)
                if not content:
                    continue
                truncated = content[:max_chars]
                grouped.setdefault(language, []).append((path, truncated))
                seen += 1
            elif item.get("type") == "dir":
                # Shallow listing of directories
                sub_items = _list_repo_paths(owner, repo, default_branch, item.get("path", ""))
                for sub in sub_items:
                    if seen >= max_files:
                        break
                    if sub.get("type") != "file":
                        continue
                    path = sub.get("path", "")
                    language = _detect_language_by_path(path)
                    if not language:
                        continue
                    content = _fetch_raw_file(owner, repo, default_branch, path)
                    if not content:
                        continue
                    truncated = content[:max_chars]
                    grouped.setdefault(language, []).append((path, truncated))
                    seen += 1
    return grouped


def analyze_code_style_from_repos(repo_links: List[str]) -> str:
    """Perform a RAG-style consolidated code style analysis from multiple GitHub repo links.

    The analysis differentiates by programming languages and synthesizes common traits across repos.
    Returns a single text with the consolidated findings.
    """
    if not repo_links:
        return "No repositories provided."

    language_to_snippets: Dict[str, List[str]] = {}
    repo_summaries: List[str] = []

    for link in repo_links:
        parsed = _parse_repo_link(link)
        if not parsed:
            continue
        owner, repo = parsed
        info = _fetch_repo_info(owner, repo)
        if not info:
            continue
        default_branch = info.get("default_branch") or "main"
        languages_bytes = _fetch_languages(owner, repo)
        top_languages = ", ".join(sorted(languages_bytes.keys())) if languages_bytes else "unknown"

        samples = _collect_repo_samples(owner, repo, default_branch)
        for language, pairs in samples.items():
            for path, content in pairs:
                language_to_snippets.setdefault(language, []).append(f"Path: {path}\n\n{content}")

        repo_summaries.append(f"- {owner}/{repo} (branch: {default_branch}) | Languages: {top_languages}")

    # Build the context with language sections
    context_sections: List[str] = []
    for language, snippets in language_to_snippets.items():
        # Limit number of snippets per language to keep prompt size manageable
        limited = snippets[:6]
        joined = "\n\n---\n\n".join(limited)
        context_sections.append(f"### Language: {language}\n\n{joined}")

    repos_overview = "\n".join(repo_summaries) if repo_summaries else "No accessible repositories."
    context_block = "\n\n".join(context_sections) if context_sections else "No code samples retrieved."

    prompt = f"""
    You are a senior code review and style analysis expert.
    You are given code samples extracted from multiple repositories, grouped by programming language.

    Your tasks:
    1. Provide a consolidated code style analysis, organized **per language** with clear headings.
    2. For each language, describe:
    - **Conventions**: naming standards, formatting, comments, file/folder structure
    - **Patterns & Architecture**: frameworks, design patterns, modularity, dependency management
    - **Code Quality**: clarity, maintainability, adherence to best practices, error handling, testing coverage
    - **Common Libraries & Tools**: frequently used dependencies or built-in features
    - **Strengths & Weaknesses**: highlight both good and bad practices found

    3. After individual analyses, provide a **cross-language comparison**:
    - Key similarities in style or architecture
    - Significant differences in approach or code quality
    - Observations about consistency across repositories

    4. Finish with an **executive summary** (4–6 lines) highlighting the most representative and recurring traits, including strengths and improvement opportunities.

    Guidelines:
    - Be objective and evidence-based; avoid speculation beyond code samples.
    - Use bullet points where possible for clarity.
    - Keep section headings clear so they are easy to parse programmatically.
    - Output in this exact structure:

    ## <Language>
    Conventions: ...
    Patterns & Architecture: ...
    Code Quality: ...
    Common Libraries & Tools: ...
    Strengths & Weaknesses: ...

    ## Cross-Language Comparison
    Similarities: ...
    Differences: ...
    Consistency Observations: ...

    ## Executive Summary
    ...

    Repositories analyzed:
    {repos_overview}

    Language context (snippets):
    {context_block}

    Answer:
    """

    return analyze(prompt)
