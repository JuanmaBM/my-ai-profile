import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == "openai":
    import openai
    openai.api_key = os.getenv("OPENAI_KEY")

elif LLM_PROVIDER == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
else:
    raise ValueError(f"Proveedor LLM no soportado: {LLM_PROVIDER}")

def analyze(prompt: str) -> str:
    if LLM_PROVIDER == "openai":
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif LLM_PROVIDER == "gemini":
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)
        return resp.text.strip()
