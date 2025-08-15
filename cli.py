import typer
import json
from pathlib import Path
from sources.linkedin import fetch_linkedin_articles
from sources.github import fetch_github_repo_links
from sources.rss import get_rss_articles_text
from analyzers.text_style import analyze_personality_text_style, analyze_writting_style
from analyzers.code_style import analyze_code_style_from_repos
from generators.markdown_gen import generate_markdown

app = typer.Typer()

@app.command()
def linkedin(user: str):
    data = fetch_linkedin_articles(user)
    texts = data.get("posts", []) if isinstance(data, dict) else (data or [])
    analysis = analyze_personality_text_style(" ".join(texts))
    Path("linkedin_analysis.json").write_text(json.dumps({"linkedin": analysis, "interests": data.get("interests", [])}))
    typer.echo("✅ LinkedIn analysis completed")


@app.command()
def github(user: str):
    repo_links = fetch_github_repo_links(user)
    analysis = analyze_code_style_from_repos(repo_links)
    Path("github_analysis.json").write_text(json.dumps({"github": analysis}))
    typer.echo("✅ GitHub analysis completed")

@app.command()
def rss(url: str, name: str):
    rss_content = get_rss_articles_text(url, 30)
    analysis = analyze_writting_style(" ".join(rss_content))
    existing_data = _load_rss_file("rss_analysis.json")
    existing_data[name] = analysis
    Path("rss_analysis.json").write_text(json.dumps(existing_data, indent=2))
    typer.echo(f"✅ RSS analysis completed for {name}")

@app.command()
def merge(user: str):
    data = {}
    
    # Load LinkedIn and GitHub analysis
    for file in ["linkedin_analysis.json", "github_analysis.json"]:
        if Path(file).exists():
            try:
                data.update(json.loads(Path(file).read_text()))
            except Exception as e:
                print(f"Error reading {file}: {e}")
    
    # Load RSS analysis
    writing_style_by_platform = _load_rss_file("rss_analysis.json")

    md = generate_markdown({
        "name": user,
        "personality": data.get("linkedin", ""),
        "writing_style": writing_style_by_platform,
        "code_style": data.get("github", ""),
        "topics": data.get("interests", [])
    })
    Path("MyAIProfile.md").write_text(md)
    typer.echo("✅ Final profile generated in MyAIProfile.md")

def _load_rss_file(file_name: str) -> dict:
    rss_file = Path(file_name)
    if rss_file.exists():
        try:
            existing_data = json.loads(rss_file.read_text())
        except Exception as e:
            print(f"Error reading existing RSS analysis: {e}")
            existing_data = {}
    else:
        existing_data = {}
    return existing_data

if __name__ == "__main__":
    app()
