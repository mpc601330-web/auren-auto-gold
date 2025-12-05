# vault/auren_affiliates_vault.py

import json
import os
from typing import Optional, Dict, Any, List


DEFAULT_VAULT_PATH = os.getenv(
    "AUREN_AFFILIATES_VAULT_PATH",
    os.path.join("vault", "affiliates_vault.json"),
)


def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {"offers": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_vault(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga el Vault desde un JSON.

    Estructura esperada:
    {
      "offers": [
        {
          "id": "curso_inversion_basica",
          "name": "Curso de Inversión para Principiantes 2025",
          "url": "https://hotmart.com/...",
          "countries": ["ES", "MX"],
          "niches": ["dinero", "inversion"],
          "keywords": ["invertir", "principiantes", "finanzas personales"],
          "slot": "default",
          "notes": "50% comisión, ticket medio 97€",
          "default_cta": "Empieza hoy tu formación en inversión desde cero."
        },
        ...
      ]
    }
    """
    return _load_json(path or DEFAULT_VAULT_PATH)


def _topic_matches_offer(topic: str, offer: Dict[str, Any]) -> int:
    """
    Devuelve un pequeño score de encaje topic ↔ oferta, basado en keywords.
    Cuanto más alto, mejor.
    """
    topic_l = topic.lower()
    score = 0

    for kw in offer.get("keywords", []):
        if kw.lower() in topic_l:
            score += 3

    for niche in offer.get("niches", []):
        if niche.lower() in topic_l:
            score += 2

    # Bonus: si el título de la oferta contiene palabras del topic
    name = offer.get("name", "").lower()
    for word in topic_l.split():
        if len(word) > 4 and word in name:
            score += 1

    return score


def pick_offer_for_video(
    topic: str,
    audience: str,
    slot: Optional[str] = None,
    country_code: Optional[str] = None,
    vault_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Selecciona la mejor oferta del Vault para este vídeo.

    - Usa keywords / niches.
    - Filtra opcionalmente por 'slot' (por ejemplo, "dinero_principiantes").
    - Filtra opcionalmente por país.
    """

    data = load_vault(vault_path)
    offers: List[Dict[str, Any]] = data.get("offers", [])

    if not offers:
        return None

    candidates: List[Dict[str, Any]] = []

    for offer in offers:
        # Filtro por slot (si se especifica)
        if slot and offer.get("slot") and offer.get("slot") != slot:
            continue

        # Filtro por país (si se especifica)
        if country_code:
            countries = offer.get("countries")
            if countries and country_code not in countries:
                continue

        score = _topic_matches_offer(topic, offer)
        if score <= 0:
            continue

        offer_copy = dict(offer)
        offer_copy["_score"] = score
        candidates.append(offer_copy)

    if not candidates:
        return None

    # Escogemos el de mejor score
    candidates.sort(key=lambda o: o["_score"], reverse=True)
    best = candidates[0]
    best.pop("_score", None)
    return best
