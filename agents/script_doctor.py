# agents/script_doctor.py
"""
AUREN_SCRIPT_DOCTOR
Transforma un guion V1 en un guion V2 profesional.

Input:
{
    "script_v1": str,
    "emotion": str,
    "platform": str,
    "audience": str,
    "style_notes": str
}

Output:
{
    "script_v2": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_SCRIPT_DOCTOR.

Eres guionista senior en una agencia premium de contenido corto
especializada en dinero, IA, afiliados y negocios digitales.

Tu trabajo:
- Recibir un guion V1 para un vídeo corto.
- Mantener la idea, pero mejorar:
  - claridad
  - ritmo
  - emoción
  - hook inicial
  - transiciones
  - cierre con CTA elegante (si aplica)

Reglas:
- Longitud objetivo: 120–220 palabras.
- Estructura:
  - Hook → Problema → Consecuencia → Solución → Cierre + CTA suave
- Frases cortas, respirables, aptas para teleprompter.
- Nada de promesas falsas ni lenguaje cutre.
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    script_v1 = input_data.get("script_v1", "").strip()
    if not script_v1:
        raise ValueError("Script Doctor: falta 'script_v1'.")

    emotion = input_data.get("emotion", "motivador")
    platform = input_data.get("platform", "TikTok / Shorts / Reels")
    audience = input_data.get("audience", "personas interesadas en dinero / IA")
    style_notes = input_data.get("style_notes", "")

    user_prompt = f"""
    Guion V1 entre ===. Mejóralo según las reglas.

    ===
    {script_v1}
    ===

    Emoción objetivo: {emotion}
    Plataforma: {platform}
    Público objetivo: {audience}

    Notas adicionales de estilo:
    {style_notes}

    Devuélveme SOLO el guion V2 final, listo para ser usado.
    """

    script_v2 = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.8,
        max_tokens=1500,
    )

    return {"script_v2": script_v2.strip()}

