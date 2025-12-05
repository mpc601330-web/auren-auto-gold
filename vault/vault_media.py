"""
vault_media.py

Módulo VAULT para Auren Media:

- Carga vault_media.json
- Devuelve la mejor oferta para un vídeo concreto
- Integra slots del Brain (affiliate_slot) + canal + país + nicho

Se usa desde auto_gold.py en la sección de afiliados.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


VAULT_PATH_DEFAULT = Path(__file__).parent / "vault_media.json"


def load_vault(path: str | None = None) -> Dict[str, Any]:
    """
    Carga el VAULT desde JSON.

    Si no se especifica path, usa vault_media.json en esta carpeta.
    """
    if path:
        p = Path(path)
    else:
        p = VAULT_PATH_DEFAULT

    if not p.is_file():
        # Mejor devolver estructura vacía que romper el pipeline
        print(f"[AUREN_VAULT] No se encontró vault_media.json en {p}. Usando VAULT vacío.")
        return {"offers": [], "channel_overrides": []}

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[AUREN_VAULT] JSON inválido en {p}: {e}. Usando VAULT vacío.")
        return {"offers": [], "channel_overrides": []}

    if not isinstance(data, dict):
        print(f"[AUREN_VAULT] Formato inválido (root no es objeto). Usando VAULT vacío.")
        return {"offers": [], "channel_overrides": []}

    data.setdefault("offers", [])
    data.setdefault("channel_overrides", [])

    return data


def _find_channel_override(
    vault: Dict[str, Any],
    channel_name: Optional[str],
    affiliate_slot: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    Busca en channel_overrides una entrada que coincida con canal y slot.
    """
    if not channel_name:
        return None

    overrides: List[Dict[str, Any]] = vault.get("channel_overrides", []) or []
    for ov in overrides:
        if ov.get("channel_name") != channel_name:
            continue
        if affiliate_slot and ov.get("affiliate_slot") == affiliate_slot:
            return ov
        # Si no hay slot, nos vale cualquier override del canal
        if not affiliate_slot:
            return ov

    return None


def _find_offer_by_id(vault: Dict[str, Any], offer_id: str) -> Optional[Dict[str, Any]]:
    offers: List[Dict[str, Any]] = vault.get("offers", []) or []
    for offer in offers:
        if offer.get("id") == offer_id:
            return offer
    return None


def _find_offer_by_slot(
    vault: Dict[str, Any],
    affiliate_slot: str,
) -> Optional[Dict[str, Any]]:
    """
    Busca una oferta cuyo default_slot coincida con affiliate_slot.
    """
    offers: List[Dict[str, Any]] = vault.get("offers", []) or []
    for offer in offers:
        if offer.get("default_slot") == affiliate_slot:
            return offer
    return None


def _find_offer_by_topic(
    vault: Dict[str, Any],
    topic: str,
    niche: str,
) -> Optional[Dict[str, Any]]:
    """
    Búsqueda muy simple por nicho y topic.
    Se puede mejorar en el futuro con embeddings / LLM.
    """
    topic_lower = topic.lower()
    niche_lower = niche.lower()

    offers: List[Dict[str, Any]] = vault.get("offers", []) or []

    # 1) Coincidencia grosera por palabras clave en nicho
    for offer in offers:
        tags = [t.lower() for t in (offer.get("tags") or [])]
        niches = [n.lower() for n in (offer.get("niches") or [])]

        if any(word in niche_lower for word in niches) or any(word in topic_lower for word in tags):
            return offer

    # 2) fallback: primera oferta
    return offers[0] if offers else None


def suggest_offer_for_video(
    vault: Dict[str, Any],
    topic: str,
    niche: str,
    country_code: str,
    channel_name: Optional[str] = None,
    affiliate_slot: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Devuelve la mejor oferta para un vídeo concreto.

    Lógica v1 (sencilla, pero funcional):

    1) Si hay override específico para canal + slot → usar esa oferta + URL custom.
    2) Si no, si hay affiliate_slot:
       - buscar oferta por default_slot == affiliate_slot
    3) Si no, buscar oferta por topic/niche.
    4) Filtrar por país si es posible.
    """
    # 1) Overrides por canal
    override = _find_channel_override(vault, channel_name, affiliate_slot)
    if override:
        offer = _find_offer_by_id(vault, str(override.get("offer_id")))
        if offer:
            # Ensamblar resultado combinado
            result = dict(offer)
            # URL final = custom_url si existe, si no base_url
            result["final_url"] = override.get("custom_url") or offer.get("base_url")
            result["source"] = "channel_override"
            return result

    # 2) Buscar por slot
    if affiliate_slot:
        offer = _find_offer_by_slot(vault, affiliate_slot)
        if offer:
            result = dict(offer)
            result["final_url"] = offer.get("base_url")
            result["source"] = "slot_match"
            return result

    # 3) Buscar por topic/niche
    offer = _find_offer_by_topic(vault, topic, niche)
    if offer:
        # 3.1) Filtrar por país (si la oferta tiene restricción)
        countries = offer.get("countries") or []
        if countries and country_code not in countries:
            # País no soportado → mejor no devolver oferta
            return None

        result = dict(offer)
        result["final_url"] = offer.get("base_url")
        result["source"] = "topic_or_niche"
        return result

    # Nada encontrado
    return None
