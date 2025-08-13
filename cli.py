import typer
import json
from pathlib import Path
from sources.linkedin import fetch_linkedin_articles
from sources.github import fetch_github_code
from analyzers.text_style import analyze_text_style
from analyzers.code_style import analyze_code_style
from generators.markdown_gen import generate_markdown

app = typer.Typer()

@app.command()
def linkedin(user: str):
    texts = fetch_linkedin_articles(user)
    analysis = analyze_text_style(" ".join(texts[:3]))
    Path("linkedin_analysis.json").write_text(json.dumps({"linkedin": analysis}))
    typer.echo("✅ Análisis LinkedIn completado.")

@app.command()
def github(user: str, repo: str):
    code_files = fetch_github_code(user, repo)
    analysis = analyze_code_style("\n".join(code_files[:2]))
    Path("github_analysis.json").write_text(json.dumps({"github": analysis}))
    typer.echo("✅ Análisis GitHub completado.")

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
    typer.echo("✅ Perfil final generado en profile.md.")

if __name__ == "__main__":
    app()
