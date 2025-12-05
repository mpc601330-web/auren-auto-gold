# agents/trend_oracle.py
from .agent_utils import run_llm

def run_agent(params: dict) -> dict:
    niche = params["niche"]
    country = params.get("country", "ES")
    notes = params.get("notes", "")

    user_prompt = f"""
    Niche: {niche}
    Country: {country}

    Contexto extra:
    {notes}

    Devuélveme:
    - 5–10 tendencias actuales relacionadas con este nicho
    - palabras clave
    - qué tipo de contenido corto funcionaría mejor
    """
    text = run_llm("Eres un analista de tendencias para contenido corto.", user_prompt)

    return {
        "trends_raw": text
    }
