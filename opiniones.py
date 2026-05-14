import requests
import pandas as pd
import re

from src.config import (
    TRAKT_CLIENT_ID
)

CLIENT_ID = TRAKT_CLIENT_ID

HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": CLIENT_ID
}


def obtener_todos_comentarios(slug):

    comentarios_totales = []
    pagina = 1

    while True:

        url = f"https://api.trakt.tv/shows/{slug}/comments"

        params = {
            "page": pagina,
            "limit": 100
        }

        response = requests.get(
            url,
            headers=HEADERS,
            params=params
        )

        comentarios = response.json()

        if not comentarios:
            break

        comentarios_totales.extend(comentarios)

        print(
            f"Página {pagina}: "
            f"{len(comentarios)} comentarios"
        )

        pagina += 1

    return comentarios_totales


def buscar_slug_trakt(nombre_serie):

    if not CLIENT_ID:
        return None

    url = "https://api.trakt.tv/search/show"

    params = {
        "query": nombre_serie,
        "fields": "title"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    if response.status_code != 200:
        return None

    resultados = response.json()

    if not resultados:
        return None

    primer = resultados[0]

    show = primer.get("show", {})

    ids = show.get("ids", {})

    return ids.get("slug")


def limpiar_texto(texto):

    # eliminar URLs
    texto = re.sub(r'http\S+|www\S+', '', texto)

    # eliminar menciones Reddit
    texto = re.sub(r'u/\w+', '', texto)

    # eliminar saltos de línea
    texto = texto.replace('\n', ' ')

    # eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)

    # quitar espacios al inicio/final
    texto = texto.strip()

    return texto


if __name__ == "__main__":

    comentarios = obtener_todos_comentarios(
        "attack-on-titan"
    )

    dataset = []

    for indice, comentario in enumerate(comentarios, start=1):

        texto = comentario.get("comment", "")

        texto_limpio = limpiar_texto(texto)

        if texto_limpio:

            dataset.append({
                "id": indice,
                "comentario": texto_limpio
            })

    df = pd.DataFrame(dataset)

    df.to_csv(
        "comentarios_limpios.csv",
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nTotal comentarios guardados: {len(df)}"
    )

    print("\nEjemplos:")

    print(df.head())
