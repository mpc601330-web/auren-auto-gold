# agents/hotmart_engine.py
"""
AUREN_HOTMART_ENGINE
Módulo placeholder para conectar con Hotmart.

Aquí todavía no llamamos a la API real,
pero dejamos la interfaz lista para integrarla.

Input:
{
    "topic": str,
    "audience": str
}

Output:
{
    "product_suggestion": str,
    "cta_idea": str
}
"""

from textwrap import dedent
from typing import Dict, Any
from .auren_llm import chat_completion

SYSTEM_PROMPT = """
Eres AUREN_HOTMART_ENGINE.

Conoces el mercado típico de productos digitales de Hotmart
(en español y portugués) sobre dinero, IA, productividad y negocios.

Tu trabajo:
- Sugerir un tipo de producto Hotmart que encaje con el tema y el público.
- Proponer una idea de CTA elegante para ese producto.

No inventes nombres concretos de cursos si no estás seguro;
habla de tipo de producto (curso de X, programa de Y, etc.).
"""


def run_agent(input_data: Dict[str, Any]) -> Dict[str, str]:
    topic = input_data.get("topic", "").strip()
    audience = input_data.get("audience", "").strip()

    if not topic:
        raise ValueError("Hotmart Engine: falta 'topic'.")

    user_prompt = f"""
    Tema del contenido:
    {topic}

    Público objetivo:
    {audience}

    1) Indica qué tipo de producto de Hotmart sería ideal.
    2) Propón una idea de CTA breve y elegante para ese producto.
    """

    suggestion = chat_completion(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=dedent(user_prompt).strip(),
        temperature=0.7,
        max_tokens=700,
    )

    return {"hotmart_suggestion_raw": suggestion.strip()}
