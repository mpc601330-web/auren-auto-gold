# auto_gold.py — ORQUESTADOR EXTERNO AUREN AUTO GOLD
# Llama (directa o indirectamente) a:
# - MIND ENGINE  → descubre topics calientes (local)
# - AUREN-API-HUB:
#       /topic_money_flow   (EMPIRE SCALER)
#       /media_plan         (MEDIA FACTORY)
#       /quality_analyze    (QUALITY ENGINE)
# - AUREN-CREATIVE-ENGINE  → genera el guion PRO (si falla → fallback local)
# - AUREN AGENTS (Groq)     → Angle Master, Script Doctor, Clip Splitter, etc.
#
# Se ejecuta fuera de Hugging (GitHub Actions o tu PC).

import os
import json
from typing import List, Dict, Any

from gradio_client import Client
import requests  # 👈 para Pexels / Pixabay
from agents.topic_scout import discover_hot_seeds
from agents.channel_router import pick_next_job
from topic_memory import mark_used
from auren_brain_adapter import load_brain_plan, pick_video_from_brain

# ==============================
# IMPORT: AUREN AGENTS (carpeta /agents)
# ==============================

# ==============================
# IMPORT: AUREN AGENTS (carpeta /agents)
# ==============================

# ------------- FÁBRICA (CREATIVE + FINAL) -------------
from agents.angle_master import run_agent as run_angle_master
from agents.script_doctor import run_agent as run_script_doctor
from agents.clip_splitter import run_agent as run_clip_splitter
from agents.title_lab import run_agent as run_title_lab
from agents.platform_translator import run_agent as run_platform_translator

# ------------- MONEY / AFILIADOS -------------
from agents.hotmart_engine import run_agent as run_hotmart_engine
from agents.saas_engine import run_agent as run_saas_engine

# ------------- CRECIMIENTO Y OPTIMIZACIÓN -------------
from agents.hook_engine import run_agent as run_hook_engine
from agents.novelty_detector import run_agent as run_novelty_detector
from agents.opportunity_scorer import run_agent as run_opportunity_scorer
from agents.content_gap_hunter import run_agent as run_content_gap_hunter
from agents.hashtag_engine import run_agent as run_hashtag_engine
from agents.description_engine import run_agent as run_description_engine

from agents.upload_scheduler import run_agent as run_upload_scheduler
from agents.retention_analyzer import run_agent as run_retention_analyzer
from agents.ctr_forecaster import run_agent as run_ctr_forecaster
from agents.content_performance import run_agent as run_content_performance

# ------------- DASHBOARD -------------
from agents.dashboard_engine import run_agent as run_dashboard_engine

# ------------- **BRAIN (NUEVOS)** -------------
from agents.trend_oracle import run_agent as run_trend_oracle
from agents.channel_evaluator import run_agent as run_channel_evaluator

# ==============================
# MAPEOS DESDE AUREN BRAIN
# ==============================

def map_emotion(brain_emotion: str) -> str:
    """
    Traduce las etiquetas del Brain a algo que entiendan los agentes.
    """
    e = (brain_emotion or "").lower()

    if "miedo" in e:
        return "Miedo (suave)"
    if "aspiracional" in e:
        return "Aspiracional"
    if "calma" in e:
        return "Calma"
    if "rabia" in e:
        return "Indignación controlada"

    # fallback genérico
    return "Motivador"


def map_platform(brain_platform: str) -> str:
    """
    Traduce 'tiktok', 'shorts', 'reels' → nombre amigable para el pipeline.
    """
    p = (brain_platform or "").lower()

    if "tiktok" in p:
        return "TikTok"
    if "short" in p:
        return "YouTube Shorts"
    if "reel" in p:
        return "Instagram Reels"

    # fallback: formato vertical corto por defecto
    return "YouTube Shorts"

# ==============================
# CONFIG: IDs de tus Spaces
# ==============================

HUB_SPACE_ID = os.getenv("AUREN_HUB_SPACE_ID", "Mariapc601/AUREN-API-HUB").strip()
CREATIVE_SPACE_ID = os.getenv("AUREN_CREATIVE_SPACE_ID", "Mariapc601/AUREN-CREATIVE-ENGINE").strip()
# Render Server (cola de vídeo)
RENDER_URL = os.getenv(
    "AUREN_RENDER_URL",
    "https://mariapc601-auren-render-server.hf.space/render_video",  # por defecto tu Space
).strip()

# Si tus Spaces son privados, usamos HF_TOKEN del entorno.
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()


def get_client(space_id: str) -> Client:
    """
    Crea un cliente gradio_client para un Space.
    Si existe HF_TOKEN, lo dejamos en la variable de entorno
    (gradio_client la usa internamente).
    """
    if HF_TOKEN:
        os.environ["HF_TOKEN"] = HF_TOKEN
    return Client(space_id)

# ============================================================
# WRAPPER para AUREN-CREATIVE-ENGINE (Space remoto)
# ============================================================

def run_creative_engine(params: dict) -> str:
    """
    Wrapper que llama al Space AUREN-CREATIVE-ENGINE
    y se asegura de que SIEMPRE haya un 'audience' válido.
    """
    audience = params.get(
        "audience",
        "jóvenes 18-30 años de España que quieren dinero y libertad usando IA y negocios online"
    )

    payload = {
        "topic": params["topic"],
        "emotion": params["emotion"],
        "platform": params["platform"],
        "audience": audience,
    }

    client = get_client(CREATIVE_SPACE_ID)

    # IMPORTANTE: aquí pasamos los 4 argumentos que espera el Space
    result = client.predict(
        payload["topic"],
        payload["emotion"],
        payload["platform"],
        payload["audience"],
    )

    if isinstance(result, str):
        return result
    return str(result)

# ============================================================
# 1) MIND ENGINE — descubrir topics a partir de un NICHO
#    (implementado localmente aquí, sin llamar a ningún Space)
# ============================================================

def mind_discover_topics(
    niche: str,
    country_code: str = "ES",
    lang: str = "es",
    n: int = 7,
) -> Dict[str, Any]:
    """
    Genera una lista de topics a partir de un NICHO.
    Esto simula tu AUREN-MIND-ENGINE pero en versión local.
    Devuelve:
      {
        "topics": [str, ...],
        "markdown": str  # bloque bonito para meter en el informe
      }
    """
    base = niche.strip()
    if not base:
        base = "dinero y libertad"

    templates = [
        f"{base} para principiantes",
        f"Errores típicos en {base}",
        f"Cómo ganar dinero con {base}",
        f"{base} explicado a niños de 12 años",
        f"Los mayores mitos sobre {base}",
        f"Historias reales de gente que cambió su vida gracias a {base}",
        f"{base} en {country_code}: oportunidades ocultas",
    ]

    topics = templates[: max(1, min(n, len(templates)))]

    # Bloque markdown para el informe
    md = [
        "# 🧠 AUREN MIND ENGINE — Discover hot topics",
        "",
        f"**Nicho:** {base}",
        "",
        f"**País objetivo:** {country_code}  |  **Idioma:** {lang}",
        "",
        "",
        "## 🎯 Temas sugeridos",
        "",
    ]
    for i, t in enumerate(topics, start=1):
        md.append(f"**{i}. {t}**")
        md.append(f"- Enfoque: explica {base} con ejemplos muy cercanos al público objetivo.")
        md.append("")

    return {"topics": topics, "markdown": "\n".join(md)}


# ============================================================
# 2) EMPIRE SCALER — money_score via HUB (/topic_money_flow)
# ============================================================

def hub_topic_money_flow(topics: List[str], lang: str = "es") -> List[Dict[str, Any]]:
    """
    Llama al endpoint /topic_money_flow del HUB y devuelve SIEMPRE una lista de dicts.
    Cada dict incluye: topic, views_30d, intent, ads_density, money_score.
    """
    client = get_client(HUB_SPACE_ID)
    topics_json = json.dumps(topics, ensure_ascii=False)

    result = client.predict(
        topics_json,
        lang,
        api_name="/topic_money_flow",
    )

    # HUB actual devuelve lista directa
    if isinstance(result, list):
        return result

    # Por si en el futuro volvemos a {"results": [...]}
    if isinstance(result, dict) and isinstance(result.get("results"), list):
        return result["results"]

    raise RuntimeError(
        f"Respuesta inesperada de topic_money_flow: tipo {type(result)} | contenido: {str(result)[:200]}"
    )


# ============================================================
# 3) MEDIA FACTORY — plan de miniatura + B-roll via HUB
# ============================================================

def hub_media_plan(script: str, want_thumb: bool, want_broll: bool) -> Dict[str, Any]:
    """
    Llama al endpoint /media_plan del HUB y normaliza la salida.
    Devuelve dict:
    {
      "plan": str | None,
      "thumbnail_plan": str | None,
      "broll_plan": str | None,
      "raw": respuesta_original
    }
    """
    client = get_client(HUB_SPACE_ID)
    result = client.predict(
        script.strip(),
        bool(want_thumb),
        bool(want_broll),
        api_name="/media_plan",
    )

    # String plano
    if isinstance(result, str):
        return {
            "plan": result,
            "thumbnail_plan": None,
            "broll_plan": None,
            "raw": result,
        }

    # Dict estructurado
    if isinstance(result, dict):
        plan = result.get("plan")
        thumb = result.get("thumbnail_plan")
        broll = result.get("broll_plan")

        if not any([plan, thumb, broll]):
            txt = json.dumps(result, ensure_ascii=False, indent=2)
            return {
                "plan": txt,
                "thumbnail_plan": None,
                "broll_plan": None,
                "raw": result,
            }

        return {
            "plan": plan,
            "thumbnail_plan": thumb,
            "broll_plan": broll,
            "raw": result,
        }

    # Tipo raro
    return {
        "plan": f"⚠️ Respuesta inesperada de /media_plan: {type(result)} | {str(result)[:200]}",
        "thumbnail_plan": None,
        "broll_plan": None,
        "raw": result,
    }


# ============================================================
# 4) QUALITY ENGINE — análisis via HUB (/quality_analyze)
# ============================================================

def hub_quality_analyze(script: str, tipo: str) -> Dict[str, Any]:
    """
    Llama al endpoint /quality_analyze del HUB y normaliza la salida.
    Devuelve dict:
    {
      "informe": str | None,
      "metrics": dict,
      "sentiment": dict,
      "suggestions": list[str]
    }
    """
    client = get_client(HUB_SPACE_ID)
    result = client.predict(
        script,
        tipo,
        api_name="/quality_analyze",
    )

    if isinstance(result, str):
        return {
            "informe": result,
            "metrics": {},
            "sentiment": {},
            "suggestions": [],
        }

    if isinstance(result, dict):
        return {
            "informe": result.get("informe"),
            "metrics": result.get("metrics", {}) or {},
            "sentiment": result.get("sentiment", {}) or {},
            "suggestions": result.get("suggestions", []) or [],
        }

    return {
        "informe": f"⚠️ Respuesta inesperada de /quality_analyze: {type(result)} | {str(result)[:200]}",
        "metrics": {},
        "sentiment": {},
        "suggestions": [],
    }


# ============================================================
# 5) CREATIVE ENGINE — guion V1 (Space + fallback local)
# ============================================================

def creative_generate_script(topic: str, emotion: str, platform: str, audience: str | None = None) -> str:
    """
    Intenta llamar al Space AUREN-CREATIVE-ENGINE.
    Si falla, usa fallback local.
    """

    # fallback de audiencia si viene vacía
    if not audience or audience.strip() == "":
        audience = "jóvenes 18-30 años de España que quieren dinero y libertad usando IA y negocios online"

    # 1) Intento normal: Space remoto
    if CREATIVE_SPACE_ID:
        try:
            result = run_creative_engine({
                "topic": topic,
                "emotion": emotion,
                "platform": platform,
                "audience": audience,
            })
            return result

        except Exception as e:
            # Log técnico solo en consola, no en el guion
            print(f"⚠️ Error llamando a AUREN-CREATIVE-ENGINE ({CREATIVE_SPACE_ID}):", e)

    # 2) FALLBACK LOCAL — Guion limpio y usable
    hook = (
        f"Nadie te explicó de verdad qué es {topic}, pero cada día que no entiendes esto,"
        " alguien gana dinero a tu costa."
    )

    script = f"""🧠 AUREN-CREATIVE-ENGINE (FALLBACK LOCAL)

{hook}

Mira, {topic} no va de hacerte rico rápido, va de entender un sistema nuevo de dinero que ya está aquí aunque hagas como que no existe.

Primero, lo simple: te explico en palabras normales qué es y qué no es {topic}, sin tecnicismos ni humo.

Luego, los errores que comete todo principiante: entrar por hype, invertir lo que no tiene y seguir consejos de gente que ni enseña su cara.

Después, la parte útil: 2–3 pasos concretos para empezar sin arruinarte, con cantidades pequeñas y reglas claras.

Y después, la verdad incómoda: si no entiendes cómo funciona el juego del dinero, siempre juegas en el equipo que pierde.

Así que la próxima vez que escuches {topic}, no huyas: respira hondo, entiende las reglas… y juega a tu favor.
"""

    return script


# ============================================================
# 6) DESCARGA AUTOMÁTICA DE CLIPS (PEXELS / PIXABAY)
# ============================================================

def download_video(url: str, save_path: str):
    """Descarga un archivo de vídeo desde una URL a la ruta indicada."""
    try:
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Error descargando {url}: {e}")
        return False


def extract_keywords_from_plan(plan: str) -> list[str]:
    """
    Extrae palabras clave del plan de B-roll automáticamente.
    Busca palabras relevantes (dinero, estrés, oficina, éxito…)
    """
    import re
    words = re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}", plan.lower())

    blacklist = {"porque", "cuando", "donde", "sobre", "según", "video", "broll", "miniatura"}
    keywords = [w for w in words if w not in blacklist]

    # Útiles como búsqueda
    return list(set(keywords))[:10]   # máximo 10


def pexels_search_and_download(keywords: list[str], target_folder: str, max_videos: int = 5):
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        print("⚠️ No PEXELS_API_KEY en GitHub Secrets")
        return []

    headers = {"Authorization": api_key}
    saved_files = []

    for kw in keywords:
        url = f"https://api.pexels.com/videos/search?query={kw}&per_page=2"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()
            for video in data.get("videos", []):
                file_url = video["video_files"][0]["link"]
                file_name = f"{kw}_{video['id']}.mp4"
                file_path = os.path.join(target_folder, file_name)
                if download_video(file_url, file_path):
                    saved_files.append(file_path)
                if len(saved_files) >= max_videos:
                    return saved_files
        except Exception:
            pass

    return saved_files


def pixabay_search_and_download(keywords: list[str], target_folder: str, max_videos: int = 5):
    api_key = os.getenv("PIXABAY_API_KEY", "")
    if not api_key:
        print("⚠️ No PIXABAY_API_KEY en GitHub Secrets")
        return []

    saved_files = []

    for kw in keywords:
        url = f"https://pixabay.com/api/videos/?key={api_key}&q={kw}&per_page=2"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for hit in data.get("hits", []):
                file_url = hit["videos"]["medium"]["url"]
                file_name = f"{kw}_{hit['id']}.mp4"
                file_path = os.path.join(target_folder, file_name)
                if download_video(file_url, file_path):
                    saved_files.append(file_path)
                if len(saved_files) >= max_videos:
                    return saved_files
        except Exception:
            pass

    return saved_files

# ============================================================
# 7) RENDER SERVER — Encola el vídeo en el Space de render
# ============================================================

def send_to_render_server(
    template_id: str,
    script_v2: str,
    platform: str,
    language: str = "es",
    audience: str | None = None,
) -> Dict[str, Any]:
    """
    Envía un job sencillo al AUREN RENDER SERVER.
    Ahora mismo solo encola el trabajo (no monta todavía el vídeo real).
    """

    if not RENDER_URL:
        return {
            "status": "disabled",
            "message": "AUREN_RENDER_URL no está configurado en el entorno.",
        }

    plat = (platform or "").lower()
    if any(x in plat for x in ["short", "tiktok", "reel", "vertical"]):
        aspect_ratio = "9:16"
        resolution = "1080x1920"
    else:
        aspect_ratio = "16:9"
        resolution = "1920x1080"

    # De momento enviamos una única escena 'talking_head' con todo el guion.
    scenes = [
        {
            "type": "talking_head",
            "duration": 60.0,  # dummy, ya lo ajustaremos
            "text": script_v2[:4000],
        }
    ]

    payload = {
        "template_id": template_id,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "fps": 30,
        "language": language,
        "voice_profile": "auren_default_female",
        "audience": audience,
        "platform": platform,
        "scenes": scenes,
        "music": {
            "mood": "motivational",
            "intensity": "medium",
        },
    }

    try:
        r = requests.post(RENDER_URL, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        data.setdefault("render_url", RENDER_URL)
        return data
    except Exception as e:
        return {
            "status": "error",
            "render_url": RENDER_URL,
            "error": str(e),
        }

# ============================================================
# 8) PIPELINE GOLD COMPLETO (ya con AGENTES AUREN)
# ============================================================

# ============================================================
# 8) PIPELINE GOLD COMPLETO (ya con AGENTES AUREN)
# ============================================================

def run_gold_pipeline(
    niche: str,
    country_code: str = "ES",
    lang_topics: str = "es",
    emotion: str = "Motivador",
    platform: str = "YouTube Shorts",
    want_thumb: bool = True,
    want_broll: bool = True,
    run_quality: bool = True,
    top_n: int = 1,
) -> str:
    """
    1) MIND: genera lista de topics a partir de un NICHO.
    2) EMPIRE: calcula money_score para cada topic (HUB /topic_money_flow).
    3) Ordena descendente por money_score.
    4) Para los TOP N:
       - Genera ángulos (AUREN_ANGLE_MASTER + HOOK_ENGINE).
       - Llama a CREATIVE (guion V1).
       - Refinado (AUREN_SCRIPT_DOCTOR → guion V2).
       - Analiza retención (RETENTION_ANALYZER).
       - Crea clips (AUREN_CLIP_SPLITTER).
       - Títulos (AUREN_TITLE_LAB).
       - Traducción por plataforma (AUREN_PLATFORM_TRANSLATOR).
       - Descripción + hashtags (DESCRIPTION_ENGINE + HASHTAG_ENGINE).
       - Hotmart + SaaS (AUREN_HOTMART_ENGINE + AUREN_SAAS_ENGINE).
       - Llama a HUB /media_plan (miniatura + B-roll) con guion V2.
       - Predicción de CTR (CTR_FORECASTER).
       - Llama a HUB /quality_analyze (QA) con guion V2.
       - Descarga clips de apoyo (Pexels / Pixabay).
       - Plan de publicación (UPLOAD_SCHEDULER).
    Devuelve un markdown grande con todo + dashboard final.
    """

    # 1) MIND — descubrir topics
    mind = mind_discover_topics(niche, country_code=country_code, lang=lang_topics)
    topics = mind["topics"]

    if not topics:
        return "⚠️ MIND ENGINE no generó topics."

    # 2) EMPIRE — money score
    money_rows = hub_topic_money_flow(topics, lang=lang_topics)

    fused = []
    for topic, row in zip(topics, money_rows):
        ms = float(row.get("money_score", 0.0) or 0.0)
        fused.append(
            {
                "topic": topic,
                "views_30d": int(row.get("views_30d", 0) or 0),
                "intent": float(row.get("intent", 0.0) or 0.0),
                "ads_density": float(row.get("ads_density", 0.0) or 0.0),
                "money_score": ms,
            }
        )

    fused.sort(key=lambda x: x["money_score"], reverse=True)
    top_n = max(1, min(top_n, len(fused)))
    top_topics = fused[:top_n]

    out: List[str] = []

    out.append("# 🟣 AUREN AUTO GOLD — RUN EXTERNO\n")
    out.append(
        "Este script se ejecuta **fuera de HuggingFace** y orquesta:\n"
        "- MIND ENGINE (topics calientes)\n"
        "- EMPIRE SCALER (money_score vía HUB)\n"
        "- CREATIVE ENGINE (guion V1)\n"
        "- AUREN AGENTS (guion V2, hooks, clips, títulos, afiliados)\n"
        "- MEDIA FACTORY (miniatura + B-roll vía HUB)\n"
        "- QUALITY ENGINE (QA vía HUB)\n"
        "- RENDER SERVER (cola lógica de vídeo)\n"
    )

    # Bloque MIND
    out.append("\n## 🧠 MIND ENGINE — Discover hot topics\n")
    out.append("```markdown")
    out.append(mind["markdown"])
    out.append("```")

    # =========================================
    # EXTRA MIND: NOVELTY + OPORTUNIDADES + GAPS
    # =========================================
    topics_list_markdown = "\n".join(f"- {t}" for t in topics)

    out.append("\n### 🧠 Extra MIND — análisis de novedad y oportunidades\n")

    # NOVELTY DETECTOR
    novelty_data = run_novelty_detector(
        {
            "topics_raw": topics_list_markdown,
        }
    )
    novelty_raw = novelty_data.get("novelty_report_raw", "").strip()

    # OPPORTUNITY SCORER
    opportunity_data = run_opportunity_scorer(
        {
            "topics_raw": topics_list_markdown,
        }
    )
    opportunity_raw = opportunity_data.get("opportunity_table_raw", "").strip()

    # CONTENT GAP HUNTER
    gap_data = run_content_gap_hunter(
        {
            "niche": niche,
            "competitor_notes": "Competencia típica de YouTube/TikTok en este nicho.",
        }
    )
    gaps_raw = gap_data.get("gaps_raw", "").strip()

    out.append("```markdown")
    out.append("#### NOVEDAD Y SATURACIÓN\n")
    out.append(novelty_raw or "⚠️ No se pudo generar análisis de novedad.")
    out.append("\n\n#### OPORTUNIDADES POR TEMA\n")
    out.append(opportunity_raw or "⚠️ No se pudo generar tabla de oportunidades.")
    out.append("\n\n#### GAPS DE CONTENIDO\n")
    out.append(gaps_raw or "⚠️ No se detectaron gaps específicos.")
    out.append("```")

    # Tabla ranking EMPIRE
    out.append("\n## 💰 Ranking de topics por money_score\n")
    out.append("| # | Topic | Views 30d | Intent % | Ads % | Money Score |\n")
    out.append("|---|-------|-----------|----------|-------|-------------|\n")
    for i, r in enumerate(fused, start=1):
        out.append(
            f"| {i} | {r['topic']} | {r['views_30d']} | "
            f"{r['intent']:.1f} | {r['ads_density']:.1f} | {r['money_score']:.1f} |"
        )

    # Detalle de los TOP
    for idx, r in enumerate(top_topics, start=1):
        topic = r["topic"]
        audience = "jóvenes que quieren ganar dinero con IA, negocios online y productividad"

        out.append("\n---\n")
        out.append(f"## 🔥 TOP {idx} — {topic}\n")
        out.append(
            f"- Money Score: **{r['money_score']:.1f}** | "
            f"Intent: **{r['intent']:.1f}%** | Ads: **{r['ads_density']:.1f}%**\n"
        )

        # ==========================
        # AUREN_ANGLE_MASTER
        # ==========================
        out.append("### 🎯 Ángulos generados (AUREN_ANGLE_MASTER)\n")
        angles_data = run_angle_master(
            {
                "topic": topic,
                "audience": audience,
                "emotion": emotion,
                "platform": platform,
                "num_angles": 12,
            }
        )
        angles_text = angles_data.get("angles_raw", "").strip()
        out.append("```markdown")
        out.append(angles_text or "⚠️ No se generaron ángulos.")
        out.append("```")

        # ==========================
        # HOOK ENGINE — hooks extra
        # ==========================
        out.append("\n### ⚡ Hooks extra (AUREN_HOOK_ENGINE)\n")
        hook_data = run_hook_engine(
            {
                "topic": topic,
                "audience": audience,
                "emotion": emotion,
                "platform": platform,
            }
        )
        hooks_raw = hook_data.get("hooks_raw", "").strip()
        out.append("```markdown")
        out.append(hooks_raw or "⚠️ No se pudieron generar hooks adicionales.")
        out.append("```")

        # ==========================
        # CREATIVE ENGINE — GUION V1
        # ==========================
        out.append("\n### 🧠 Guion V1 generado (AUREN-CREATIVE-ENGINE)\n")
        topic_with_angles = (
            f"{topic}\n\nÁngulos sugeridos:\n{angles_text}" if angles_text else topic
        )
        script_v1 = creative_generate_script(
            topic_with_angles,
            emotion,
            platform,
            audience=audience,
        )

        out.append("```markdown")
        out.append(script_v1)
        out.append("```")

        # ==========================
        # SCRIPT DOCTOR — GUION V2
        # ==========================
        out.append("\n### ✍️ Guion V2 refinado (AUREN_SCRIPT_DOCTOR)\n")
        script_v2_dict = run_script_doctor(
            {
                "script_v1": script_v1,
                "emotion": emotion,
                "platform": platform,
                "audience": audience,
                "style_notes": "Tono profesional, cercano, elegante, energía Pendragon.",
            }
        )
        script_v2 = script_v2_dict.get("script_v2", script_v1)
        out.append("```markdown")
        out.append(script_v2)
        out.append("```")

        # ==========================
        # RETENTION ANALYZER
        # ==========================
        out.append("\n### 📈 Retención estimada (AUREN_RETENTION_ANALYZER)\n")
        retention_data = run_retention_analyzer(
            {
                "script_v2": script_v2,
            }
        )
        retention_raw = retention_data.get("retention_report_raw", "").strip()
        out.append("```markdown")
        out.append(retention_raw or "⚠️ No se generó informe de retención.")
        out.append("```")

        # ==========================
        # CLIP SPLITTER — CLIPS
        # ==========================
        out.append("\n### 🎬 Clips generados (AUREN_CLIP_SPLITTER)\n")
        clips_dict = run_clip_splitter(
            {
                "script_v2": script_v2,
                "min_clips": 7,
                "max_clips": 12,
            }
        )
        clips_raw = clips_dict.get("clips_raw", "").strip()
        out.append("```markdown")
        out.append(clips_raw or "⚠️ No se pudieron generar clips.")
        out.append("```")

        # ==========================
        # TITLE LAB
        # ==========================
        out.append("\n### 🏷️ Títulos sugeridos (AUREN_TITLE_LAB)\n")
        titles_dict = run_title_lab(
            {
                "clip_text": script_v2,
                "platform": platform,
            }
        )
        titles_raw = titles_dict.get("titles_raw", "").strip()
        out.append("```markdown")
        out.append(titles_raw or "⚠️ No se generaron títulos.")
        out.append("```")

        # ==========================
        # PLATFORM TRANSLATOR
        # ==========================
        out.append("\n### 🌍 Adaptación por plataforma (AUREN_PLATFORM_TRANSLATOR)\n")
        platform_dict = run_platform_translator(
            {
                "clip_text": script_v2,
            }
        )
        platform_versions_raw = platform_dict.get("platform_versions_raw", "").strip()
        out.append("```markdown")
        out.append(
            platform_versions_raw
            or "⚠️ No se generaron versiones por plataforma."
        )
        out.append("```")

        # ==========================
        # DESCRIPTION ENGINE + HASHTAG ENGINE
        # ==========================
        out.append(
            "\n### 📝 Descripción y hashtags (AUREN_DESCRIPTION_ENGINE + AUREN_HASHTAG_ENGINE)\n"
        )

        desc_data = run_description_engine(
            {
                "script_v2": script_v2,
                "topic": topic,
                "niche": niche,
            }
        )
        description_raw = desc_data.get("description_raw", "").strip()

        hashtag_data = run_hashtag_engine(
            {
                "topic": topic,
                "niche": niche,
                "language": lang_topics,
            }
        )
        hashtags_raw = hashtag_data.get("hashtags_raw", "").strip()

        out.append("```markdown")
        out.append("#### Descripción sugerida\n")
        out.append(description_raw or "⚠️ No se generó descripción.")
        out.append("\n\n#### Hashtags sugeridos\n")
        out.append(hashtags_raw or "⚠️ No se generaron hashtags.")
        out.append("```")

        # ==========================
        # AFFILIATES: HOTMART + SaaS
        # ==========================
        out.append(
            "\n### 💸 Encaje de afiliados (AUREN_HOTMART_ENGINE + AUREN_SAAS_ENGINE)\n"
        )

        hotmart_data = run_hotmart_engine(
            {
                "topic": topic,
                "audience": audience,
            }
        )
        hotmart_raw = hotmart_data.get("hotmart_suggestion_raw", "").strip()

        saas_data = run_saas_engine(
            {
                "topic": topic,
                "audience": audience,
            }
        )
        saas_raw = saas_data.get("saas_suggestion_raw", "").strip()

        out.append("```markdown")
        out.append("#### Hotmart\n")
        out.append(hotmart_raw or "⚠️ Sin sugerencia Hotmart.")
        out.append("\n\n#### SaaS recurrente\n")
        out.append(saas_raw or "⚠️ Sin sugerencia SaaS.")
        out.append("```")

        # ==========================
        # MEDIA PLAN (con GUION V2)
        # ==========================
        out.append("\n### 🎥 Plan de producción (HUB /media_plan)\n")
        media = hub_media_plan(script_v2, want_thumb=want_thumb, want_broll=want_broll)
        if media.get("plan"):
            out.append(media["plan"])
        if want_thumb and media.get("thumbnail_plan"):
            out.append("\n#### 🖼️ Bloque Miniatura\n")
            out.append(media["thumbnail_plan"])
        if want_broll and media.get("broll_plan"):
            out.append("\n#### 🎬 Bloque B-Roll\n")
            out.append(media["broll_plan"])

            # ==========================
            #  DESCARGA AUTOMÁTICA DE CLIPS
            # ==========================
            assets_folder = f"videos/assets_{topic.replace(' ', '_')}"
            os.makedirs(assets_folder, exist_ok=True)

            # 1) Extraer keywords del plan de B-roll
            kw = extract_keywords_from_plan(media.get("broll_plan", ""))

            # 2) Descargar desde Pexels
            pex_files = pexels_search_and_download(kw, assets_folder)

            # 3) Descargar desde Pixabay
            pix_files = pixabay_search_and_download(kw, assets_folder)

            out.append("\n### 🎞️ Clips descargados automáticamente\n")
            out.append(f"- Pexels: {len(pex_files)} vídeos")
            out.append(f"- Pixabay: {len(pix_files)} vídeos")

        # ==========================
        # CTR FORECASTER (título + miniatura)
        # ==========================
        out.append("\n### 🎯 Predicción de CTR (AUREN_CTR_FORECASTER)\n")

        first_title = ""
        if titles_raw:
            for line in titles_raw.splitlines():
                line = line.strip()
                if line and not line.startswith(("#", "-", "*")):
                    first_title = line
                    break

        thumb_brief_text = media.get("thumbnail_plan") or media.get("plan") or ""

        ctr_data = run_ctr_forecaster(
            {
                "title": first_title,
                "thumbnail_brief": thumb_brief_text,
            }
        )
        ctr_raw = ctr_data.get("ctr_forecast_raw", "").strip()

        out.append("```markdown")
        out.append(ctr_raw or "⚠️ No se pudo estimar el CTR.")
        out.append("```")

        # ==========================
        # UPLOAD SCHEDULER
        # ==========================
        out.append(
            "\n### 🗓 Plan de publicación recomendado (AUREN_UPLOAD_SCHEDULER)\n"
        )
        upload_plan = run_upload_scheduler(
            {
                "audience": audience,
                "timezone": "Europe/Madrid",
            }
        )
        upload_raw = upload_plan.get("upload_plan_raw", "").strip()

        out.append("```markdown")
        out.append(upload_raw or "⚠️ No se generó plan de publicación.")
        out.append("```")

        # ==========================
        # QUALITY ENGINE (sobre GUION V2)
        # ==========================
        if run_quality:
            if (
                "short" in platform.lower()
                or "tiktok" in platform.lower()
                or "reels" in platform.lower()
            ):
                tipo = "Short motivacional (rápido)"
            elif "long" in platform.lower():
                tipo = "Vídeo largo storytelling"
            else:
                tipo = "Vídeo educativo"

            out.append(f"\n### 🧪 Análisis de calidad (QUALITY ENGINE — {tipo})\n")
            q = hub_quality_analyze(script_v2, tipo)
            if q.get("informe"):
                out.append(q["informe"])

        # ==========================
        # RENDER SERVER — Encolar vídeo
        # ==========================
        out.append("\n### 🧩 Render job (AUREN RENDER SERVER)\n")
        render_res = send_to_render_server(
            template_id="motivacional_v1",
            script_v2=script_v2,
            platform=platform,
            language=lang_topics,
            audience=audience,
        )
        out.append("```json")
        out.append(json.dumps(render_res, ensure_ascii=False, indent=2))
        out.append("```")

    # ==========================
    # DASHBOARD ENGINE — resumen ejecutivo del run
    # ==========================
    full_markdown = "\n".join(out)

    # Limitamos el tamaño para no romper el límite de tokens de Groq
    max_chars = 6000
    if len(full_markdown) > max_chars:
        dashboard_input = full_markdown[-max_chars:]
    else:
        dashboard_input = full_markdown

    dashboard_data = run_dashboard_engine(
        {
            "inputs_raw": dashboard_input,
        }
    )
    dashboard_raw = dashboard_data.get("dashboard_summary_raw", "").strip()

    out.append("\n---\n")
    out.append("## 📊 Resumen ejecutivo (AUREN_DASHBOARD_ENGINE)\n")
    out.append("```markdown")
    out.append(dashboard_raw or "⚠️ No se generó resumen ejecutivo.")
    out.append("```")

    return "\n".join(out)


def main():
    # ¿Hay plan de Auren Brain?
    brain_plan_path = os.getenv("AUREN_BRAIN_PLAN_PATH", "").strip()

    if brain_plan_path:
        # ============================
        # 🎛️ MODO CONTROLADO POR BRAIN
        # ============================
        plan = load_brain_plan(brain_plan_path)
        video_cfg = pick_video_from_brain(plan)

        if not video_cfg:
            print("⚠️ Auren Brain no devolvió ningún vídeo. Saliendo.")
            return

        print("🧠 Auren Brain activo:")
        print("   Canal:", video_cfg["channel_name"])
        print("   Topic:", video_cfg["topic"])
        print("   Video ID:", video_cfg["video_id"])
        print("   Emoción:", video_cfg["emotion"])
        print("   Plataforma:", video_cfg["target_platform"])

        niche = video_cfg["topic"]
        country_code = video_cfg["country"]
        lang_topics = video_cfg["language"]

        emotion = map_emotion(video_cfg["emotion"])
        platform = map_platform(video_cfg["target_platform"])
        want_thumb = True
        want_broll = True
        run_quality = True
        top_n = 1

        markdown = run_gold_pipeline(
            niche=niche,
            country_code=country_code,
            lang_topics=lang_topics,
            emotion=emotion,
            platform=platform,
            want_thumb=want_thumb,
            want_broll=want_broll,
            run_quality=run_quality,
            top_n=top_n,
        )

        # Opcional: aquí podrías pasar también info del Brain al nombre del fichero
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        os.makedirs("outputs", exist_ok=True)
        md_path = f"outputs/auren_gold_{ts}.md"
        json_path = f"outputs/auren_gold_{ts}.json"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"output": markdown}, ensure_ascii=False, indent=2))

        print(f"\n💾 Guardado en: {md_path} y {json_path}")

        os.makedirs("videos", exist_ok=True)
        video_plan_path = f"videos/video_plan_{ts}.md"

        video_plan_content = (
            "# 🎬 AUREN VIDEO PLAN\n\n"
            "## 📝 Guion + Producción\n\n"
            f"{markdown}\n"
        )

        with open(video_plan_path, "w", encoding="utf-8") as f:
            f.write(video_plan_content)

        print(f"📦 Plan de vídeo guardado en: {video_plan_path}")
        return

    # ============================
    # 🔁 MODO ANTIGUO (AutoGold solo)
    # ============================
    seeds = discover_hot_seeds()
    job = pick_next_job(seeds)

    if not job:
        print("⚠️ No hay temas nuevos disponibles (todas las semillas ya se usaron).")
        return

    channel = job["channel"]
    seed = job["seed"]
    topic_slug = job["topic_slug"]

    print("🧠 Canal seleccionado:", channel["name"])
    print("🌱 Semilla seleccionada:", seed.keyword)
    print("🪪 Topic slug:", topic_slug)

    niche = seed.keyword
    country_code = channel["country"]
    lang_topics = channel["language"]

    emotion = "Motivador"
    platform = "YouTube Shorts"
    want_thumb = True
    want_broll = True
    run_quality = True
    top_n = 1

    markdown = run_gold_pipeline(
        niche=niche,
        country_code=country_code,
        lang_topics=lang_topics,
        emotion=emotion,
        platform=platform,
        want_thumb=want_thumb,
        want_broll=want_broll,
        run_quality=run_quality,
        top_n=top_n,
    )

    print(markdown)
    mark_used(channel["id"], topic_slug)

    os.makedirs("outputs", exist_ok=True)
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    md_path = f"outputs/auren_gold_{ts}.md"
    json_path = f"outputs/auren_gold_{ts}.json"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"output": markdown}, ensure_ascii=False, indent=2))

    print(f"\n💾 Guardado en: {md_path} y {json_path}")

    os.makedirs("videos", exist_ok=True)
    video_plan_path = f"videos/video_plan_{ts}.md"

    video_plan_content = (
        "# 🎬 AUREN VIDEO PLAN\n\n"
        "## 📝 Guion + Producción\n\n"
        f"{markdown}\n"
    )

    with open(video_plan_path, "w", encoding="utf-8") as f:
        f.write(video_plan_content)

    print(f"📦 Plan de vídeo guardado en: {video_plan_path}")


if __name__ == "__main__":
    main()


