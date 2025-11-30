# auto_gold.py — ORQUESTADOR EXTERNO AUREN AUTO GOLD
# Llama a:
# - AUREN-API-HUB: topic_money_flow, media_plan, quality_analyze
# - AUREN-CREATIVE-ENGINE: genera guion PRO
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
CREATIVE_SPACE_ID = os.getenv("AUREN_CREATIVE_SPACE_ID", "Mariapc601/AUREN-CREATIVE-ENGINE").strip()

# Si tus Spaces son privados, usamos HF_TOKEN del entorno.
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()


def get_client(space_id: str) -> Client:
    """
    Crea un cliente gradio_client para un Space.
    Algunas versiones no aceptan hf_token como parámetro,
    así que, si existe, lo dejamos en la variable de entorno HF_TOKEN
    (gradio_client ya la sabe usar internamente).
    """
    if HF_TOKEN:
        os.environ["HF_TOKEN"] = HF_TOKEN

    return Client(space_id)


# ==============================
# HELPERS: llamadas al HUB
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
# HELPER: CREATIVE ENGINE
# ==============================

def creative_generate_script(topic: str, emotion: str, platform: str) -> str:
    """
    Llama al Space AUREN-CREATIVE-ENGINE.
    Ese Space tiene un solo botón, así que usamos predict() sin api_name.
    Orden de inputs: idea, emotion, platform.
    """
    client = get_client(CREATIVE_SPACE_ID)
    result = client.predict(
        topic,     # idea
        emotion,   # emotion dropdown
        platform,  # platform dropdown
    )
    if isinstance(result, str):
        return result
    return str(result)


# ==============================
# PIPELINE GOLD COMPLETO
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
) -> str:
    """
    1) Calcula money_score para cada topic (HUB /topic_money_flow)
    2) Ordena descendente por money_score
    3) Para los TOP N:
       - Llama a CREATIVE (guion)
       - Llama a HUB /media_plan (miniatura + B-roll)
       - Llama a HUB /quality_analyze (QA)
    Devuelve un markdown grande con todo.
    """
    if not topics:
        return "⚠️ No hay topics."

    # 1) Money score
    money_rows = hub_topic_money_flow(topics, lang=lang_topics)

    fused = []
    for topic, row in zip(topics, money_rows):
        ms = float(row.get("money_score", 0.0) or 0.0)
        fused.append({
            "topic": topic,
            "views_30d": int(row.get("views_30d", 0) or 0),
            "intent": float(row.get("intent", 0.0) or 0.0),
            "ads_density": float(row.get("ads_density", 0.0) or 0.0),
            "money_score": ms,
        })

    fused.sort(key=lambda x: x["money_score"], reverse=True)
    top_n = max(1, min(top_n, len(fused)))
    top_topics = fused[:top_n]

    out: List[str] = []

    out.append("# 🟣 AUREN AUTO GOLD — RUN EXTERNO\n")
    out.append(
        "Este script se ejecuta **fuera de HuggingFace** y orquesta:\n"
        "- EMPIRE (money_score via HUB)\n"
        "- CREATIVE (guion)\n"
        "- MEDIA FACTORY (miniatura + B-roll via HUB)\n"
        "- QUALITY (QA via HUB)\n"
    )

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
            if "short" in platform.lower() or "tiktok" in platform.lower() or "reels" in platform.lower():
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
# ENTRYPOINT
# ==============================

def main():
    # ==========================
    # CONFIG RÁPIDA DEL RUN
    # (puedes cambiar estos topics cuando quieras)
    # ==========================
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
    lang_topics = "es"
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
    )

    # Imprimimos el resultado en consola (Actions lo guardará en logs)
    print(markdown)


if __name__ == "__main__":
    main()
