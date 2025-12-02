import os
from typing import List, Dict, Union
from groq import Groq

# Modelo por defecto de Groq (puedes cambiarlo por otro si quieres)
DEFAULT_GROQ_MODEL = os.getenv("AUREN_GROQ_MODEL", "llama-3.1-70b-versatile")


def _get_client() -> Groq:
    """
    Crea el cliente Groq usando la API key del entorno.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta GROQ_API_KEY en las variables de entorno / GitHub Secrets."
        )
    return Groq(api_key=api_key)


def _chat_with_messages(
    messages: List[Dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Llamada básica a Groq usando una lista de mensajes.
    """
    client = _get_client()
    model_name = model or DEFAULT_GROQ_MODEL

    resp = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def chat_completion(
    system_or_messages: Union[str, List[Dict[str, str]]],
    user_prompt: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """
    Wrapper flexible que usan los agentes.

    Se puede llamar de dos formas:

    1) chat_completion(system_prompt, user_prompt)
    2) chat_completion(messages=[{"role": "...", "content": "..."}])

    Internamente siempre construimos una lista de messages para Groq.
    """
    # Caso 2: ya nos pasan messages
    if isinstance(system_or_messages, list):
        messages = system_or_messages

    else:
        # Caso 1: system_prompt + user_prompt
        system_prompt = system_or_messages
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
