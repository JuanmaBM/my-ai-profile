from llm_client import analyze


def analyze_text_style(text: str) -> str:
    prompt = f"""
    Analyze the following text and describe:
    - Personality traits
    - Writing style (formality, vocabulary, emotional tone)

    Text: {text}
    """
    return analyze(prompt)
