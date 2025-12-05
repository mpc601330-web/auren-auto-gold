# forge/render_forge.py

import os
import glob
import time
from typing import Dict, Any, Optional, List

from moviepy.editor import VideoFileClip, concatenate_videoclips


def _slugify(text: str) -> str:
    """
    Convierte un texto en un slug simple para nombres de fichero.
    """
    text = text.lower().strip()
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    out = []
    for ch in text.replace(" ", "-"):
        if ch in allowed:
            out.append(ch)
        else:
            out.append("-")
    # quitar dobles guiones
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "video"


def build_vertical_video_from_assets(
    assets_folder: str,
    output_path: str,
    max_duration: Optional[int] = 60,
    target_height: int = 1920,
    target_width: int = 1080,
) -> Dict[str, Any]:
    """
    Construye un vídeo vertical sencillo concatenando los clips .mp4 de assets_folder.

    - Ajusta todos los clips a resolución vertical 1080x1920.
    - Recorta centrado en horizontal si hace falta.
    - Corta la duración total a max_duration segundos (si se indica).
    """

    if not os.path.isdir(assets_folder):
        raise FileNotFoundError(f"Carpeta de assets no encontrada: {assets_folder}")

    pattern = os.path.join(assets_folder, "*.mp4")
    files = sorted(glob.glob(pattern))

    if not files:
        raise RuntimeError(f"No se encontraron vídeos .mp4 en {assets_folder}")

    clips: List[VideoFileClip] = []
    total_duration = 0.0

    for path in files:
        clip = VideoFileClip(path)

        # Redimensionar a altura fija manteniendo proporción
        clip = clip.resize(height=target_height)

        # Si sobra anchura, recortamos centrado para dejar 1080
        if clip.w > target_width:
            x_center = clip.w / 2
            x1 = x_center - target_width / 2
            x2 = x_center + target_width / 2
            clip = clip.crop(x1=x1, x2=x2)

        # Limitamos duración total (si se pasa max_duration)
        if max_duration is not None and total_duration + clip.duration > max_duration:
            remaining = max_duration - total_duration
            if remaining <= 0:
                clip.close()
                break
            clip = clip.subclip(0, remaining)

        clips.append(clip)
        total_duration += clip.duration

        if max_duration is not None and total_duration >= max_duration:
            break

    if not clips:
        raise RuntimeError("No se pudieron usar clips válidos para el montaje.")

    final = concatenate_videoclips(clips, method="compose")

    # Exporta el vídeo final
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        codec="libx264",
        audio=False,        # de momento sin audio; luego conectaremos TTS
        fps=30,
        threads=4,
        preset="medium",
    )

    # Liberar memoria
    for c in clips:
        c.close()
    final.close()

    return {
        "status": "ok",
        "output_path": output_path,
        "num_clips": len(clips),
        "total_duration": total_duration,
    }


def run_local_render(
    template_id: str,
    script_v2: str,
    platform: str,
    language: str,
    audience: str,
    assets_folder: str,
) -> Dict[str, Any]:
    """
    Render Forge local:
    - Usa los vídeos ya descargados en assets_folder.
    - Genera un vídeo vertical final en videos/rendered/.
    - Devuelve un diccionario estilo "render job" para el markdown.
    """

    slug = _slugify(template_id or "auren_video")
    ts = int(time.time())
    output_dir = os.path.join("videos", "rendered")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{slug}_{ts}.mp4")

    render_info = build_vertical_video_from_assets(
        assets_folder=assets_folder,
        output_path=output_path,
        max_duration=60,      # Shorts / Reels
    )

    # Enriquecemos el resultado con contexto
    render_info.update(
        {
            "template_id": template_id,
            "platform": platform,
            "language": language,
            "audience": audience,
        }
    )

    return render_info
