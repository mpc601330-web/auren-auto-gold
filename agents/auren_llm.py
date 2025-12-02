# agents/auren_llm.py
"""
Núcleo LLM compartido para TODOS los agentes de Auren.

Usa Groq como backend compatible OpenAI.

🔧 Requisitos:
- pip install openai

🔐 Secrets / variables de entorno recomendadas:
- GROQ_API_KEY (obligatoria)
- OPENAI_BASE_URL="https://api.groq.com/openai/v1" (opcional, por si quieres sobreescribir)
"""

import os
from typing import List, Dict
from openai import OpenAI

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")

if not GROQ_API_KEY:
    raise RuntimeError(
        "❌ Falta GROQ_API_KEY en las variables de entorno / Secrets del Space."
    )

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url=BASE_URL,
)

DEFAULT_MODEL = os.getenv("AUREN_LLM_MODEL", "llama-3.1-70b-versatile")


def chat_completion(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1500,
) -> str:
    """
    Helper básico para chat.completions.

    Devuelve solo el contenido de la respuesta.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()
