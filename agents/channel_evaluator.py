# agents/channel_evaluator.py
from .agent_utils import run_llm

def run_agent(params: dict) -> dict:
    channel_name = params["channel_name"]
    last_results = params.get("last_results", "")

    user_prompt = f"""
    Canal: {channel_name}

    Datos recientes (resumen manual o copia de un reporte):
    {last_results}

    Analiza:
    - qué tipo de vídeos están funcionando mejor (tema, tono, duración, hook)
    - qué está fallando
    - qué deberíamos hacer más
    - qué deberíamos dejar de hacer
    """
    text = run_llm(
        "Eres un analista de rendimiento de canales de contenido corto.",
        user_prompt
    )

    return {
        "channel_report_raw": text
    }
