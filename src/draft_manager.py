import json
from pathlib import Path

DRAFT_DIR = Path("data/borradores")


def normalizar_nombre(titulo):
    if not titulo:
        return ""
    return titulo.lower().replace(" ", "_").replace("/", "-").replace("\\", "-")


def obtener_ruta_draft(titulo):
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    nombre = normalizar_nombre(titulo)
    return DRAFT_DIR / f"{nombre}_draft.json"


def existe_draft(titulo):
    return obtener_ruta_draft(titulo).exists()


def crear_draft(documento, titulo, datos=None):
    ruta = obtener_ruta_draft(titulo)

    contenido = {
        "id": documento.get("id"),
        "titulo": titulo,
        "texto": documento.get("texto", ""),
        "notas": "",
        "metadata": datos.get("tmdb", {}) if datos else {},
        "personajes": datos.get("personajes", []) if datos else [],
        "wikipedia": datos.get("wikipedia", {}) if datos else {},
        "slug": datos.get("slug") if datos else None,
    }

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(contenido, f, ensure_ascii=False, indent=2)

    return ruta


def leer_draft(titulo):
    ruta = obtener_ruta_draft(titulo)
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def reconstruir_documento(draft):
    if draft.get("texto"):
        return {
            "id": draft.get("id"),
            "texto": draft["texto"]
        }

    return {
        "id": draft.get("id"),
        "texto": draft.get("texto", "")
    }
