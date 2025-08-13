from llm_client import analyze

def analyze_code_style(code: str) -> str:
    prompt = f"""
    Analiza el siguiente código y describe:
    - Convenciones usadas (nombres, indentación, comentarios)
    - Patrones de diseño detectados
    - Nivel de claridad y mantenibilidad
    Código:
    {code}
    """
    return analyze(prompt)
