# =====================================
# AUREN CHANNEL EVALUATOR
# Analiza rendimiento y estrategias del canal
# Devuelve un bloque normalizado con claves:
#   - evaluation_raw
# =====================================

from agents.agent_utils import run_llm

SYSTEM_PROMPT = """
Eres AUREN CHANNEL EVALUATOR.
Tu misión es analizar un canal como si fueras un consultor experto en crecimiento digital.

Reglas:
- Identifica patrones.
- Indica qué formatos funcionan.
- Indica qué debe eliminarse.
- Recomendaciones claras, sin ruido.
- Nada de "depende".
- Propuestas accionables que Auren Brain pueda usar para tomar decisiones.

Formato final:
# EVALUACIÓN DEL CANAL
## Estado general:
- ...

## Qué está funcionando:
- ...

## Qué NO está funcionando:
- ...

## Recomendaciones:
- ...

## Oportunidades de escalado:
- ...

## Riesgos del canal:
- ...
"""

def run_agent(inputs: dict) -> dict:
    """
    inputs = {
        "channel_name": str,
        "last_30_markdown": str   # resumen de rendimiento si lo tienes
    }
    """

    channel = inputs.get("channel_name", "Canal desconocido")
    history = inputs.get("last_30_markdown", "")

    user_prompt = f"""
Analiza este canal: {channel}

Historial / Notas últimas 30 piezas:
{history}

Dame un análisis profesional completo.
"""

    try:
        text = run_llm(SYSTEM_PROMPT, user_prompt)
    except Exception as e:
        text = f"⚠️ Error evaluando canal: {e}"

    return {
        "evaluation_raw": text.strip()
    }

