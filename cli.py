import typer
import json
from pathlib import Path
from sources.linkedin import fetch_linkedin_articles
from sources.github import fetch_github_repo_links
from analyzers.text_style import analyze_text_style
from analyzers.code_style import analyze_code_style_from_repos
from generators.markdown_gen import generate_markdown

app = typer.Typer()

@app.command()
def linkedin(user: str):
    texts = fetch_linkedin_articles(user)
    analysis = analyze_text_style(" ".join(texts[:3]))
    Path("linkedin_analysis.json").write_text(json.dumps({"linkedin": analysis}))
    typer.echo("✅ LinkedIn analysis completed")


@app.command()
def github(user: str):
    repo_links = fetch_github_repo_links(user)
    analysis = analyze_code_style_from_repos(repo_links)
    Path("github_analysis.json").write_text(json.dumps({"github": analysis}))
    typer.echo("✅ GitHub analysis completed")


@app.command()
def merge():
    data = {}
    for file in ["linkedin_analysis.json", "github_analysis.json"]:
        if Path(file).exists():
            data.update(json.loads(Path(file).read_text()))
    md = generate_markdown({
        "name": "Usuario",
        "personality": data.get("linkedin", ""),
        "writing_style": data.get("linkedin", ""),
        "code_style": data.get("github", ""),
        "topics": ["IA", "Open Source"]
    })
    Path("profile.md").write_text(md)
    typer.echo("✅ Final profile generated in profile.md")

if __name__ == "__main__":
    app()
