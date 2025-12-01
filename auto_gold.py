# auto_gold.py — ORQUESTADOR EXTERNO AUREN AUTO GOLD
# Llama (directa o indirectamente) a:
# - MIND ENGINE  → descubre topics calientes (local)
# - AUREN-API-HUB:
#       /topic_money_flow   (EMPIRE SCALER)
#       /media_plan         (MEDIA FACTORY)
#       /quality_analyze    (QUALITY ENGINE)
# - AUREN-CREATIVE-ENGINE  → genera el guion PRO (si falla → fallback local)
#
# Se ejecuta fuera de Hugging (GitHub Actions o tu PC).

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
    Si existe HF_TOKEN, lo dejamos en la variable de entorno
    (gradio_client la usa internamente).
    """
    if HF_TOKEN:
        os.environ["HF_TOKEN"] = HF_TOKEN
    return Client(space_id)


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
# 5) CREATIVE ENGINE — guion PRO (Space + fallback local)
# ============================================================

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
# 6) PIPELINE GOLD COMPLETO
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
       - Llama a CREATIVE (guion).
       - Llama a HUB /media_plan (miniatura + B-roll).
       - Llama a HUB /quality_analyze (QA).
    Devuelve un markdown grande con todo.
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
        "- MIND ENGINE (topics calientes)\n"
        "- EMPIRE SCALER (money_score vía HUB)\n"
        "- CREATIVE ENGINE (guion)\n"
        "- MEDIA FACTORY (miniatura + B-roll vía HUB)\n"
        "- QUALITY ENGINE (QA vía HUB)\n"
    )

    # Bloque MIND
    out.append("\n## 🧠 MIND ENGINE — Discover hot topics\n")
    out.append("```markdown")
    out.append(mind["markdown"])
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
    # CONFIG RÁPIDA DEL RUN
    niche = "dinero y libertad"
    country_code = "ES"
    lang_topics = "es"

    emotion = "Motivador"
    platform = "YouTube Shorts"
    want_thumb = True
    want_broll = True
    run_quality = True
    top_n = 1  # cuántos TOP quieres procesar a fondo

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

    # Imprimimos el resultado en consola (Actions lo guardará en logs)
    print(markdown)

    # ==========================
    #  GUARDADO AUTOMÁTICO
    # ==========================

    # Creamos carpeta /outputs si no existe
    os.makedirs("outputs", exist_ok=True)

    # Nombre bonito con timestamp
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    md_path = f"outputs/auren_gold_{ts}.md"
    json_path = f"outputs/auren_gold_{ts}.json"

    # Guardar Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Guardar JSON simple
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"output": markdown}, ensure_ascii=False, indent=2))

    print(f"\n💾 Guardado en: {md_path} y {json_path}")


if __name__ == "__main__":
    main()



