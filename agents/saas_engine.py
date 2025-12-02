# agents/saas_engine.py
"""
AUREN_SAAS_ENGINE
Sugiere un SaaS ideal + ángulo de afiliado.

Input:
{
    "topic": str,
    "audience": str
}

Output:
{
    "saas_suggestion": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_SAAS_ENGINE.

Tu trabajo:
- Dado un tema y un público, sugerir el tipo de herramienta SaaS ideal
  (por ejemplo: gestor de tareas, CRM, herramienta de IA, editor de vídeo, etc.)
- Proponer un ángulo para promocionarla como afiliado:
  - dolor que resuelve
  - beneficio principal
  - idea de CTA suave

No hace falta decir nombres exactos de herramientas, solo el tipo y ángulo.
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    topic = input_data.get("topic", "").strip()
    audience = input_data.get("audience", "").strip()

    if not topic:
        raise ValueError("SaaS Engine: falta 'topic'.")

    user_prompt = f"""
    Tema del contenido:
    {topic}

    Público objetivo:
    {audience}

    Sugiere:
    - Tipo de SaaS ideal
    - Cómo encajaría en el contenido
    - Un posible ángulo de afiliado (resumen).
    """

    suggestion = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.7,
        max_tokens=700,
    )

    return {"saas_suggestion_raw": suggestion.strip()}
