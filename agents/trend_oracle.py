# =====================================
# AUREN TREND ORACLE
# Analiza tendencias actuales para nicho / país / plataforma
# Devuelve un bloque normalizado con claves:
#   - trends_raw
# =====================================

from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN TREND ORACLE, un analista profesional de tendencias digitales.
Tu tarea es detectar señales, patrones y oportunidades reales.

Reglas:
- Sé concreto, claro, accionable.
- NO inventes datos numéricos falsos.
- Sí puedes inferir patrones de comportamiento.
- Escribe en estilo ejecutivo, como un informe real.
- Devuelve siempre insights listos para usar en una fábrica de contenidos.

Formato final:
# TENDENCIAS
- Momentum:
- Qué está subiendo:
- Qué está bajando:
- Señales tempranas:
- Oportunidades accionables:
"""

def run_agent(inputs: dict) -> dict:
    """
    inputs = {
        "niche": str,
        "country": str,
        "platform": str
    }
    """

    niche = inputs.get("niche", "")
    country = inputs.get("country", "ES")
    platform = inputs.get("platform", "youtube")

    user_prompt = f"""
Nicho: {niche}
País: {country}
Plataforma: {platform}

Genera un análisis completo de tendencias para este contexto.
"""

    try:
        text = run_llm(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        text = f"⚠️ Error generando tendencias: {e}"

    return {
        "trends_raw": text.strip()
    }

