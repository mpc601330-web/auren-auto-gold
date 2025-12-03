# agents/agent_utils.py
from typing import Dict, Any
from agents.auren_llm import chat_completion


def run_llm(system_prompt: str, user_prompt: str, extra: Dict[str, Any] | None = None) -> str:
    """
    Helper genérico para llamar al LLM de Auren.

    Lo dejamos simple a propósito: si cambias la implementación
    de chat_completion en auren_llm.py, solo tocas aquí.
    """
    if extra is None:
        extra = {}

    # NOTA: adapta estos parámetros a la firma real de chat_completion
    # si hace falta. Mientras no uses estos agentes, no afectan al resto.
    return chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        **extra,
    )
