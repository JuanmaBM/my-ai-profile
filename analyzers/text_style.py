from llm_client import analyze

def analyze_text_style(text: str) -> str:
    prompt = f"""
    Analiza el siguiente texto y describe:
    - Rasgos de personalidad
    - Estilo de escritura (formalidad, vocabulario, tono emocional)
    Texto: {text}
    """
    return analyze(prompt)
