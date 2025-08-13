import os
import requests
from typing import List


def fetch_github_code(user: str, repo: str):
    # Simulación: en producción usar PyGithub
    return [
        "def ejemplo():\n    print('Hola mundo')",
        "class Ejemplo:\n    pass"
    ]


def fetch_github_repo_links(user: str) -> List[str]:
    """Return the html_url links of all public repositories for a user.

    Uses GitHub's public API and paginates through results to collect all of them.
    If the environment variable `GITHUB_TOKEN` exists, it will be used to increase the rate limit.
    """
    base_url = f"https://api.github.com/users/{user}/repos"
    headers = {}
    # token = os.getenv("GITHUB_TOKEN")
    # if token:
    #     headers["Authorization"] = f"token {token}"

    params = {"per_page": 100, "type": "public", "sort": "updated"}
    links: List[str] = []
    url = base_url

    while url:
        response = requests.get(url, headers=headers, params=params if "?" not in url else None, timeout=15)
        if response.status_code != 200:
            break

        repos = response.json() or []
        for repo in repos:
            if not repo.get("private"):
                html_url = repo.get("html_url")
                if html_url:
                    links.append(html_url)

        # Pagination: look for the "next" link in the Link header
        link_header = response.headers.get("Link", "")
        next_url = None
        if link_header:
            for part in link_header.split(","):
                section = part.split(";")
                if len(section) < 2:
                    continue
                link_part = section[0].strip()
                rel_part = section[1].strip()
                if rel_part == 'rel="next"':
                    next_url = link_part[1:-1] if link_part.startswith("<") and link_part.endswith(">") else None
                    break

        url = next_url
        params = None  # after the first request, the URL already includes query params

    return links
