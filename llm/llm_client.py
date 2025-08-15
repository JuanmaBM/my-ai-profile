import os
from typing import Optional

from langchain_openai import ChatOpenAI

_LLM: Optional[ChatOpenAI] = None


def _get_llm() -> ChatOpenAI:
    """Initialize and cache a LangChain ChatOpenAI client using env vars.

    Required:
    - LLM_API_KEY: API token
    Optional:
    - LLM_BASE_URL: Base URL for the OpenAI-compatible endpoint (e.g., https://api.openai.com/v1)
    - LLM_MODEL: Model name (default: gpt-4o-mini)
    """
    global _LLM
    if _LLM is not None:
        return _LLM

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("LLM_API_KEY is required to initialize the LLM client.")

    _LLM = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )
    return _LLM


def analyze(prompt: str) -> str:
    """Run a single-turn analysis with the configured LLM and return the text output."""
    llm = _get_llm()
    # Use invoke() to avoid deprecation of predict()
    result = llm.invoke(prompt)
    # result can be a BaseMessage; get .content
    content = getattr(result, "content", None)
    return (content if isinstance(content, str) else str(result)).strip()
