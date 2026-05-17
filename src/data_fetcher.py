import re

from api import (
    buscar_serie,
    obtener_detalles,
    obtener_personajes,
    sanitizar_tmdb
)

from src.config import (
    TMDB_API_KEY
)

from .wikipedia_fetcher import (
    obtener_articulo_completo
)


def seleccionar_resultado_tmdb(resultados):
    if not resultados:
        return None
    return resultados[0]


def extraer_slug_trakt(datos_tmdb):
    if not datos_tmdb:
        return None
    titulo = datos_tmdb.get("name", "").strip().lower()
    titulo = re.sub(r"[^a-z0-9\s-]", "", titulo)
    titulo = re.sub(r"\s+", "-", titulo)
    titulo = re.sub(r"-+", "-", titulo)
    return titulo


def obtener_datos_serie(nombre_serie):
    if not TMDB_API_KEY:
        print("TMDB_API_KEY no configurado.")
        return None
    resultado = buscar_serie(nombre_serie)
    if not resultado or not resultado.get("results"):
        print("No se encontraron resultados en TMDB")
        return None
    seleccionado = seleccionar_resultado_tmdb(resultado["results"])
    tv_id = seleccionado.get("id")
    if not tv_id:
        print("No se pudo obtener TV ID")
        return None
    detalles = obtener_detalles(tv_id)
    informacion_limpia = sanitizar_tmdb(detalles)
    personajes = obtener_personajes(tv_id)
    slug = extraer_slug_trakt(seleccionado)
    wikipedia = {}
    titulo_wikipedia = informacion_limpia.get("titulo") or nombre_serie
    try:
        wikipedia = obtener_articulo_completo(titulo_wikipedia)
    except Exception as e:
        print(f"Error obteniendo Wikipedia: {e}")
    return {
        "tmdb": informacion_limpia,
        "personajes": personajes,
        "wikipedia": wikipedia,
        "slug": slug
    }