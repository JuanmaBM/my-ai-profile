from llm_client import analyze


def analyze_personality_text_style(text: str) -> str:
    prompt = f"""
    Your objetive is create a profile of the person based on the text.
    You are an expert in psycholinguistic analysis.
    Analyze the following text and provide a detailed but concise description of:

    1. Personality traits (based on language patterns: openness, conscientiousness, extroversion, agreeableness, emotional stability)
    2. Emotional tone (positive, neutral, negative — explain briefly)
    3. Feelings or moods the writer might be experiencing
    4. Communication style (direct, indirect, assertive, diplomatic, humorous, ironic, etc.)
    5. Possible underlying motivations or intent (only based on language cues, avoid guessing facts outside the text)
    6. Confidence level (High, Medium, Low — based on text clarity and length)

    Guidelines:
    - Focus only on what can be inferred from the text.
    - Avoid speculation beyond linguistic evidence.
    - Output in this exact format:

    ## Personality Traits
    ...
    ## Emotional Tone
    ...
    ## Feelings
    ...
    ## Communication Style
    ...
    ## Motivations/Intent
    ...
    ## Confidence Level
    ...

    Text to analyze:
    \"\"\"{text}\"\"\"
    """
    return analyze(prompt)

def analyze_writting_style(text: str) -> str:
    prompt = f"""
    Your objetive is create a profile of the writing style based on the text.
    You are an expert in content analysis for articles and blog posts.
    Analyze the following text and describe:

    1. Level of formality (informal, semi-formal, formal — explain briefly)
    2. Vocabulary characteristics (e.g., simple and accessible, technical and specialized, marketing-oriented — give examples)
    3. Writing style type (informative, persuasive, promotional, storytelling, educational — justify your choice)
    4. Structure and organization (e.g., clear introduction-body-conclusion, use of headings, logical flow, coherence)
    5. Use of evidence and references (e.g., data, examples, quotes — describe how effectively they are used)
    6. Engagement techniques (e.g., rhetorical questions, calls to action, humor, relatable anecdotes)
    7. Reader targeting (identify possible target audience based on tone, complexity, and examples used)

    Guidelines:
    - Focus only on what can be inferred from the text.
    - Avoid speculating about the author's personal intentions beyond what is shown in the writing.
    - Output in this exact format:

    ## Formality
    ...
    ## Vocabulary
    ...
    ## Writing Style
    ...
    ## Structure & Organization
    ...
    ## Evidence & References
    ...
    ## Engagement Techniques
    ...
    ## Reader Targeting
    ...

    Text to analyze:
    \"\"\"{text}\"\"\"
    """
    return analyze(prompt)

