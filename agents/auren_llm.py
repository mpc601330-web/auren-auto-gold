import os
from typing import List, Dict, Union
from groq import Groq

# =========================
#  CONFIGURACIÓN DEL MODELO
# =========================

# Modelo por defecto de Groq (puedes cambiarlo por otro vía variable de entorno)
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Cliente global reutilizable
_client: Groq | None = None


def _get_client() -> Groq:
    """
    Crea (o reutiliza) el cliente de Groq usando la API key del entorno.
    Lanza un error claro si falta la clave.
    """
    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY en las variables de entorno / GitHub Secrets."
        )

    _client = Groq(api_key=api_key)
    return _client


def _chat_with_messages(
    messages: List[Dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Llamada básica a Groq usando una lista de mensajes.
    La usan los agentes internos.
    """
    client = _get_client()
    model_name = model or DEFAULT_MODEL

    resp = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Groq devuelve el contenido en resp.choices[0].message.content
    return resp.choices[0].message.content.strip()


def chat_completion(
    system_prompt: Union[str, List[Dict[str, str]]],
    user_prompt: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Wrapper flexible que usan los agentes.

    Formas de uso:

      1) chat_completion(system_prompt="...", user_prompt="...")
      2) chat_completion(system_prompt=[{"role": "...", "content": "..."}])

    - Si `system_prompt` es una lista, se asume que ya es la lista completa de mensajes.
    - Si es un string, se construye la conversación con system + user.
    """

    # Caso 2: ya nos pasan messages (lista de dicts)
    if isinstance(system_prompt, list):
        messages = system_prompt  # type: ignore[assignment]

    else:
        # Caso 1: system_prompt (str) + user_prompt (str)
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if user_prompt:
            messages.append({"role": "user", "content": user_prompt})

    return _chat_with_messages(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


