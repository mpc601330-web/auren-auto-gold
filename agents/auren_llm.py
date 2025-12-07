import os
from typing import List, Dict, Union
from groq import Groq, RateLimitError  # 👈 importamos también RateLimitError

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

    👉 Devuelve SIEMPRE un string:
       - Respuesta normal del modelo
       - O un texto de error controlado empezando por:
         - 'ERROR_RATE_LIMIT:'
         - 'ERROR_LLM:'
    """
    client = _get_client()
    model_name = model or DEFAULT_MODEL

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # Groq devuelve el contenido en resp.choices[0].message.content
        return resp.choices[0].message.content.strip()

    except RateLimitError as e:
        # ⚠️ Límite diario de tokens alcanzado: NO rompemos el pipeline
        print(f"⚠️ Groq RateLimitError en _chat_with_messages: {e}")
        return (
            "ERROR_RATE_LIMIT: El modelo de Groq ha alcanzado el límite diario de tokens. "
            "Este texto es un fallback automático desde agents/auren_llm.py. "
            "Los agentes que intenten parsear esta respuesta deben tratarla como error suave."
        )

    except Exception as e:
        # Cualquier otro error de red / API → también devolvemos texto controlado
        print(f"⚠️ Error genérico llamando a Groq en _chat_with_messages: {e}")
        return (
            f"ERROR_LLM: No se ha podido llamar al modelo de Groq. "
            f"Detalle técnico: {e}"
        )


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

    👉 Siempre devuelve un string (normal o de error).
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
