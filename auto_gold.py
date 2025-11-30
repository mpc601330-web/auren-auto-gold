# auto_gold.py — ORQUESTADOR EXTERNO AUREN AUTO GOLD
# Llama a:
# - AUREN-API-HUB: mind_run, topic_money_flow, media_plan, quality_analyze
# - AUREN-CREATIVE-ENGINE: genera guion PRO (si falla → fallback local)
#
# Se ejecuta fuera de Hugging (por GitHub Actions o desde tu PC).

import os
import json
from typing import List, Dict, Any

from gradio_client import Client

# ==============================
# CONFIG: IDs de tus Spaces
# ==============================

HUB_SPACE_ID = os.getenv("AUREN_HUB_SPACE_ID", "Mariapc601/AUREN-API-HUB").strip()
CREATIVE_SPACE_ID = os.getenv(
    "AUREN_CREATIVE_SPACE_ID", "Mariapc601/AUREN-CREATIVE-ENGINE"
).strip()

# Si tus Spaces son privados, usamos HF_TOKEN del entorno.
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()


def get_client(space_id: str) -> Client:
    """
    Crea un cliente gradio_client para un Space.
    Si existe HF_TOKEN, lo dejamos en la variable de entorno,
    gradio_client ya sabe usarlo internamente.
    """
    if HF_TOKEN:
        os.environ["HF_TOKEN"] = HF_TOKEN

    # Esto permite usar tanto "repo_id" (Mariapc601/SPACE)
    # como URL completa de la API (https://xxxxx.hf.space)
    return Client(space_id)


# ==============================
# 1) MIND ENGINE (HUB /mind_run)
# ==============================

def hub_mind_discover_topics(
    niche: str,
    country: str = "ES",
    language: str = "es",
    top_k: int = 7,
) -> Dict[str, Any]:
    """
    Llama al endpoint /mind_run del HUB en modo "Discover hot topics".
    Devuelve:
      {
        "markdown": str,            # salida completa de MIND ENGINE
        "topics": [str, ...]        # lista de topics parseados
      }
    """
    niche = (niche or "").strip()
    if not niche:
        return {"markdown": "", "topics": []}

    client = get_client(HUB_SPACE_ID)
    mode = "Discover hot topics"
    manual_topics = ""

    md = client.predict(
        mode,
        niche,
        manual_topics,
        country,
        language,
        int(top_k),
        api_name="/mind_run",
    )

    if not isinstance(md, str):
        md = str(md)

    # Parsear líneas tipo: **1. tema**
    topics: List[str] = []
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("**") and ". " in line:
            inner = line.strip("*")  # quita los **
            parts = inner.split(". ", 1)
            if len(parts) == 2:
                title = parts[1].strip()
                if title:
                    topics.append(title)

    return {"markdown": md, "topics": topics}


# ==============================
# 2) EMPIRE SCALER (HUB /topic_money_flow)
# ==============================

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


# ==============================
# 3) MEDIA FACTORY (HUB /media_plan)
# ==============================

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


# ==============================
# 4) QUALITY ENGINE (HUB /quality_analyze)
# ==============================

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


# ==============================
# 5) CREATIVE ENGINE (Space + fallback)
# ==============================

def creative_generate_script(topic: str, emotion: str, platform: str) -> str:
    """
    Intenta llamar al Space AUREN-CREATIVE-ENGINE.
    Si falla (404, privado, token, etc.), NO revienta el pipeline:
    devuelve un guion completo generado por fallback local.
    """
    # 1) Intento normal: Space remoto
    if CREATIVE_SPACE_ID:
        try:
            client = get_client(CREATIVE_SPACE_ID)
            result = client.predict(
                topic,     # idea
                emotion,   # emotion dropdown
                platform,  # platform dropdown
            )
            if isinstance(result, str):
                return result
            return str(result)
        except Exception as e:
            # Log técnico solo en consola, no en el guion
            print(
                f"⚠️ Error llamando a AUREN-CREATIVE-ENGINE ({CREATIVE_SPACE_ID}):",
                e,
            )

    # 2) FALLBACK LOCAL — Guion limpio y usable
    hook = (
        f"Nadie te explicó de verdad qué es {topic}, "
        "pero cada día que no entiendes esto, alguien gana dinero a tu costa."
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


# ==============================
# 6) PIPELINE GOLD COMPLETO
# ==============================

def run_gold_pipeline(
    topics: List[str],
    emotion: str = "Motivador",
    platform: str = "YouTube Shorts",
    want_thumb: bool = True,
    want_broll: bool = True,
    run_quality: bool = True,
    lang_topics: str = "es",
    top_n: int = 1,
    mind_markdown: str | None = None,
) -> str:
    """
    1) Calcula money_score para cada topic (HUB /topic_money_flow)
    2) Ordena descendente por money_score
    3) Para los TOP N:
       - CREATIVE (guion)
       - MEDIA FACTORY (miniatura + B-roll via HUB)
       - QUALITY (QA via HUB)
    Devuelve un markdown grande con todo.
    """
    if not topics:
        return "⚠️ No hay topics."

    # 1) Money score
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
        "- MIND ENGINE (topics calientes vía HUB)\n"
        "- EMPIRE SCALER (money_score vía HUB)\n"
        "- CREATIVE ENGINE (guion)\n"
        "- MEDIA FACTORY (miniatura + B-roll vía HUB)\n"
        "- QUALITY ENGINE (QA vía HUB)\n"
    )

    # Bloque MIND ENGINE (si existe)
    if mind_markdown:
        out.append("\n## 🧠 MIND ENGINE — Discover hot topics\n")
        out.append("```markdown")
        out.append(mind_markdown)
        out.append("```")

    # Tabla ranking
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
        out.append("\n---\n")
        out.append(f"## 🔥 TOP {idx} — {topic}\n")
        out.append(
            f"- Money Score: **{r['money_score']:.1f}** | "
            f"Intent: **{r['intent']:.1f}%** | Ads: **{r['ads_density']:.1f}%**\n"
        )

        # CREATIVE
        out.append("### 🧠 Guion generado (AUREN-CREATIVE-ENGINE)\n")
        script = creative_generate_script(topic, emotion, platform)
        out.append("```markdown")
        out.append(script)
        out.append("```")

        # MEDIA PLAN
        out.append("\n### 🎥 Plan de producción (HUB /media_plan)\n")
        media = hub_media_plan(script, want_thumb=want_thumb, want_broll=want_broll)
        if media.get("plan"):
            out.append(media["plan"])
        if want_thumb and media.get("thumbnail_plan"):
            out.append("\n#### 🖼️ Bloque Miniatura\n")
            out.append(media["thumbnail_plan"])
        if want_broll and media.get("broll_plan"):
            out.append("\n#### 🎬 Bloque B-Roll\n")
            out.append(media["broll_plan"])

        # QUALITY
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
            q = hub_quality_analyze(script, tipo)
            if q.get("informe"):
                out.append(q["informe"])

    return "\n".join(out)


# ==============================
# 7) ENTRYPOINT
# ==============================

def main():
    # ==========================
    # CONFIG RÁPIDA DEL RUN
    # ==========================

    # 1) Config de MIND ENGINE
    USE_MIND_ENGINE = True
    mind_niche = "dinero y libertad"
    mind_country = "ES"
    mind_language = "es"
    mind_top_k = 7

    mind_md = ""
    topics: List[str] = []

    if USE_MIND_ENGINE:
        mind_result = hub_mind_discover_topics(
            niche=mind_niche,
            country=mind_country,
            language=mind_language,
            top_k=mind_top_k,
        )
        mind_md = mind_result.get("markdown", "") or ""
        topics = mind_result.get("topics", []) or []

    # 2) Si MIND falla o no devuelve nada, usamos una lista manual
    if not topics:
        topics = [
            "criptomonedas para principiantes",
            "teletrabajo y productividad",
            "historias de millonarios fracasados",
        ]

    emotion = "Motivador"
    platform = "YouTube Shorts"
    want_thumb = True
    want_broll = True
    run_quality = True
    lang_topics = mind_language or "es"
    top_n = 1  # cuántos TOP quieres procesar a fondo

    markdown = run_gold_pipeline(
        topics=topics,
        emotion=emotion,
        platform=platform,
        want_thumb=want_thumb,
        want_broll=want_broll,
        run_quality=run_quality,
        lang_topics=lang_topics,
        top_n=top_n,
        mind_markdown=mind_md,
    )

    # Imprimimos el resultado en consola (Actions lo guardará en logs)
    print(markdown)


if __name__ == "__main__":
    main()


