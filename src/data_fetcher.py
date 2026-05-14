import re

from api import (
    buscar_serie,
    obtener_detalles,
    obtener_personajes,
    sanitizar_tmdb
)

from opiniones import (
    buscar_slug_trakt,
    obtener_todos_comentarios,
    limpiar_texto
)

from src.config import (
    TMDB_API_KEY,
    TRAKT_CLIENT_ID
)


def seleccionar_resultado_tmdb(resultados):

    if not resultados:
        return None

    return resultados[0]


def extraer_slug_trakt(datos_tmdb):

    if not datos_tmdb:
        return None

    titulo = datos_tmdb.get("name", "").strip().lower()

    titulo = re.sub(
        r"[^a-z0-9\s-]",
        "",
        titulo
    )

    titulo = re.sub(
        r"\s+",
        "-",
        titulo
    )

    titulo = re.sub(
        r"-+",
        "-",
        titulo
    )

    return titulo


def construir_dataset_comentarios(comentarios):

    dataset = []

    for indice, comentario in enumerate(comentarios, start=1):

        texto = comentario.get("comment", "")

        texto_limpio = limpiar_texto(texto)

        if texto_limpio:

            dataset.append({
                "id": indice,
                "comentario": texto_limpio
            })

    return dataset


def obtener_datos_serie(nombre_serie):

    if not TMDB_API_KEY:
        print("TMDB_API_KEY no configurado.")
        return None

    resultado = buscar_serie(nombre_serie)

    if not resultado or not resultado.get("results"):
        return None

    seleccionado = seleccionar_resultado_tmdb(
        resultado["results"]
    )

    tv_id = seleccionado.get("id")

    if not tv_id:
        return None

    detalles = obtener_detalles(
        tv_id
    )

    informacion_limpia = sanitizar_tmdb(
        detalles
    )

    personajes = obtener_personajes(
        tv_id
    )

    slug = buscar_slug_trakt(
        nombre_serie
    )

    if not slug:
        slug = extraer_slug_trakt(
            seleccionado
        )

    comentarios = []

    if slug and TRAKT_CLIENT_ID:
        comentarios = obtener_todos_comentarios(
            slug
        )

    dataset_comentarios = construir_dataset_comentarios(
        comentarios
    )

    return {
        "tmdb": informacion_limpia,
        "personajes": personajes,
        "comentarios": dataset_comentarios,
        "slug": slug
    }
