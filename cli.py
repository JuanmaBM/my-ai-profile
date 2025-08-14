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
    data = fetch_linkedin_articles(user)
    texts = data.get("posts", []) if isinstance(data, dict) else (data or [])
    analysis = analyze_text_style(" ".join(texts))
    Path("linkedin_analysis.json").write_text(json.dumps({"linkedin": analysis, "interests": data.get("interests", [])}))
    typer.echo("✅ LinkedIn analysis completed")


@app.command()
def github(user: str):
    repo_links = fetch_github_repo_links(user)
    analysis = analyze_code_style_from_repos(repo_links)
    Path("github_analysis.json").write_text(json.dumps({"github": analysis}))
    typer.echo("✅ GitHub analysis completed")

@app.command()
def merge(user: str):
    data = {}
    for file in ["linkedin_analysis.json", "github_analysis.json"]:
        if Path(file).exists():
            data.update(json.loads(Path(file).read_text()))
    md = generate_markdown({
        "name": user,
        "personality": data.get("linkedin", ""),
        # TODO: add new source for writing style
        # "writing_style": data.get("linkedin", ""),
        "code_style": data.get("github", ""),
        "topics": data.get("interests", [])
    })
    Path("MyAIProfile.md").write_text(md)
    typer.echo("✅ Final profile generated in MyAIProfile.md")

if __name__ == "__main__":
    app()
