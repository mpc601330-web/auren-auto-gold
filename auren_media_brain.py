# auren_media_brain.py
"""
🧠 AUREN MEDIA BRAIN — Versión PRO (V1 stub)
-------------------------------------------
Este módulo es la "mente estratégica" de Auren Media.

Flujo:
1) Recibe:
   - info de canales
   - nicho / seed
   - opcional: historial / métricas

2) Pasa por 5 niveles:
   - Nivel 1: Inputs (tendencias, rendimiento, afiliados)
   - Nivel 2: Modelos internos (scoring)
   - Nivel 3: Agentes operativos (Trend Oracle, Channel Judge, etc.)
   - Nivel 4: Salida JSON para Auto Gold
   - Nivel 5: Bucle de aprendizaje (a futuro: escribe feedback)

3) Devuelve un dict (JSON) con la ORDEN para generar un vídeo.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import math
import re
from datetime import datetime


# ==========================================
# 🟦 NIVELES 1 y 2 — MODELOS / INPUTS (stub)
# ==========================================

@dataclass
class ChannelInfo:
    name: str
    niche: str
    platform: str  # "youtube", "tiktok", etc.
    ctr: float     # 0–100
    retention: float  # 0–100
    growth: float  # 0–100
    revenue: float # relativo (0–100)
    rpm: float     # estimado 0–100
    engagement: float  # 0–100


@dataclass
class TopicCandidate:
    topic: str
    base_money_score: float  # lo que venga de EMPIRE-SCALER / money_score
    novelty: float           # 0–100
    competition: float       # 0–100 (alto = mucha competencia)
    emotion: str             # "peligro_urgencia", "esperanza", etc.


def simple_topic_score(t: TopicCandidate) -> float:
    """
    Modelo de Topic Scoring simplificado.
    Combina money_score + novelty – competition.
    Más adelante se puede sustituir por algo más serio
    (regresión, RL, etc.).
    """
    money = t.base_money_score         # 0–100
    novelty = t.novelty                # 0–100
    comp = t.competition               # 0–100

    # Queremos:
    # - money alto
    # - novelty medio/alto
    # - competencia razonable (no ultra saturado)
    score = 0.5 * money + 0.3 * novelty - 0.2 * comp

    # clamp
    return max(0.0, min(100.0, round(score, 1)))


def simple_channel_score(c: ChannelInfo) -> float:
    """
    Modelo de Channel Evaluation simplificado.
    Combina CTR + retención + crecimiento + RPM.
    """
    score = (
        0.25 * c.ctr
        + 0.25 * c.retention
        + 0.25 * c.growth
        + 0.25 * c.rpm
    )
    return max(0.0, min(100.0, round(score, 1)))


def classify_channel(score: float) -> str:
    """
    GOD / GOOD / MID / DEAD según score.
    """
    if score >= 80:
        return "GOD"
    if score >= 60:
        return "GOOD"
    if score >= 40:
        return "MID"
    return "DEAD"


# ==========================================
# 🟧 NIVELES 3 y 4 — AGENTES + SALIDA JSON
# ==========================================

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[áàä]", "a", text)
    text = re.sub(r"[éèë]", "e", text)
    text = re.sub(r"[íìï]", "i", text)
    text = re.sub(r"[óòö]", "o", text)
    text = re.sub(r"[úùü]", "u", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "topic"


def pick_script_style(topic: TopicCandidate, channel: ChannelInfo) -> str:
    """
    Decide estilo de guion según tema/canal.
    Stub sencillo.
    """
    t = topic.topic.lower()
    if "historia" in t or "historias" in t:
        return "story_gold"
    if "niños" in t or "12 años" in t or "joven" in t:
        return "didactico_joven_gold"
    if "invertir" in t or "dinero" in t:
        return "cinematic_gold"
    # fallback
    return "default_gold"


def pick_voice(topic: TopicCandidate, channel: ChannelInfo) -> str:
    """
    Selecciona perfil de voz.
    """
    if "psicologia" in channel.niche.lower():
        return "female_soft"
    if "dinero" in channel.niche.lower():
        return "female_elegant"
    return "neutral_voice"


def pick_thumbnail_style(topic: TopicCandidate) -> str:
    emo = topic.emotion
    if emo == "peligro_urgencia":
        return "red_black_alert"
    if emo == "esperanza":
        return "blue_gold_hope"
    return "default_clean"


def guess_affiliate_tag(topic: TopicCandidate, channel: ChannelInfo) -> str:
    """
    Match simplificado de afiliado según nicho.
    Más adelante esto se conecta al Vault real.
    """
    t = topic.topic.lower()
    n = channel.niche.lower()

    if "invertir" in t or "dinero" in t or "financ" in n:
        return "curso_inversion_principiantes_2025"
    if "procrastinar" in t or "productividad" in t:
        return "curso_productividad_2025"
    if "psicologia" in n:
        return "saas_habitos_mente"
    return "generic_auren_offer"


def build_ai_scene_prompt(topic: TopicCandidate, channel: ChannelInfo) -> str:
    """
    Prompt cinematográfico base para la escena principal.
    """
    t = topic.topic.lower()
    if "invertir" in t:
        return (
            "young adult looking at charts on a laptop, soft golden light, "
            "night city in the background, cinematic, hope + discipline, 4k"
        )
    if "niños" in t:
        return (
            "kid counting coins on a wooden table, warm morning light, "
            "parents blurred in the background smiling, cinematic, 4k"
        )
    # fallback genérico
    return (
        "person walking alone at dawn, empty city streets, soft golden light, "
        "cinematic, feeling of change and determination, 4k"
    )


def choose_platforms(channel: ChannelInfo) -> List[str]:
    if channel.platform == "youtube":
        return ["youtube_shorts"]
    if channel.platform == "tiktok":
        return ["tiktok"]
    # multi-plataforma por defecto
    return ["youtube_shorts", "tiktok", "reels"]


# ==========================================
# 🟥 NIVEL 5 — BUCLE (stub)
# ==========================================

def record_brain_decision(decision: Dict[str, Any]) -> None:
    """
    Aquí en el futuro:
    - guardar en DB
    - escribir a un log
    - alimentar un modelo de aprendizaje

    Por ahora, lo dejamos como stub.
    """
    # TODO: conectar con tu sistema de logs / DB
    pass


# ==========================================
# 🟣 ORQUESTADOR PRINCIPAL DEL BRAIN
# ==========================================

def run_media_brain_once(
    channels: List[ChannelInfo],
    topics: List[TopicCandidate],
) -> Dict[str, Any]:
    """
    Función principal del BRAIN.

    Recibe:
      - lista de canales disponibles (con métricas)
      - lista de temas candidatos (ya enriquecidos con money_score, etc.)

    Devuelve:
      - dict con el "plan de vídeo" para Auto Gold.
    """

    if not channels:
        raise ValueError("Debe haber al menos un canal definido para el Brain.")

    if not topics:
        raise ValueError("Debe haber al menos un topic candidato para el Brain.")

    # 1) Scoring de canales
    channel_scores = []
    for ch in channels:
        s = simple_channel_score(ch)
        channel_scores.append((ch, s))

    # Escogemos el mejor canal (por ahora; luego se puede ponderar por nicho)
    channel_scores.sort(key=lambda x: x[1], reverse=True)
    best_channel, best_channel_score = channel_scores[0]
    best_channel_label = classify_channel(best_channel_score)

    # 2) Scoring de topics
    topic_scores = []
    for tc in topics:
        ts = simple_topic_score(tc)
        topic_scores.append((tc, ts))

    topic_scores.sort(key=lambda x: x[1], reverse=True)
    best_topic, best_topic_score = topic_scores[0]

    # 3) Decisiones de estilo, voz, miniatura, afiliado, etc.
    script_style = pick_script_style(best_topic, best_channel)
    voice = pick_voice(best_topic, best_channel)
    thumb_style = pick_thumbnail_style(best_topic)
    affiliate_tag = guess_affiliate_tag(best_topic, best_channel)
    scene_prompt = build_ai_scene_prompt(best_topic, best_channel)
    platforms = choose_platforms(best_channel)

    topic_slug = slugify(best_topic.topic)

    clips_needed = 7 if len(best_topic.topic) < 80 else 9  # regla tonta por ahora

    decision = {
        "channel": best_channel.name,
        "topic": best_topic.topic,
        "topic_slug": topic_slug,
        "script_style": script_style,
        "emotion": best_topic.emotion,
        "voice": voice,
        "thumbnail_style": thumb_style,
        "affiliate_tag": affiliate_tag,
        "clips_needed": clips_needed,
        "platforms": platforms,
        "ai_scene_prompt": scene_prompt,
        "brain_meta": {
            "topic_score": best_topic_score,
            "money_score": best_topic.base_money_score,
            "novelty_score": best_topic.novelty,
            "competition": best_topic.competition,
            "channel_score": best_channel_score,
            "channel_priority": best_channel_label,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "reason": (
                f"Canal '{best_channel.name}' clasificado como {best_channel_label} "
                f"y topic '{best_topic.topic}' con score alto en money + novelty."
            ),
        },
    }

    # Nivel 5 — registrar decisión (stub)
    record_brain_decision(decision)

    return decision
