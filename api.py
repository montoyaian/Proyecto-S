import requests
import json
import re

from src.config import (
    TMDB_API_KEY
)

API_KEY = TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def buscar_serie(nombre):

    url = f"{BASE_URL}/search/tv"

    params = {
        "api_key": API_KEY,
        "query": nombre,
        "language": "es-ES"
    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    return response.json()

def obtener_personajes(tv_id):

    url = f"{BASE_URL}/tv/{tv_id}/credits"

    params = {
        "api_key": API_KEY,
        "language": "es-ES"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    personajes = []

    for p in data["cast"]:

        personaje = re.sub(
            r"\s*\(voice\)",
            "",
            p["character"],
            flags=re.IGNORECASE
        )

        personajes.append(personaje)

    # eliminar duplicados
    personajes = list(
        dict.fromkeys(personajes)
    )

    return personajes

def obtener_detalles(tv_id):

    url = f"{BASE_URL}/tv/{tv_id}"

    params = {
        "api_key": API_KEY,
        "language": "es-ES"
    }

    response = requests.get(
        url,
        params=params
    )

    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    return response.json()


def sanitizar_tmdb(data):

    limpio = {

        "id": data.get("id"),

        "titulo": data.get(
            "name"
        ),

        "titulo_original": data.get(
            "original_name"
        ),

        "descripcion": data.get(
            "overview"
        ),

        "fecha_estreno": data.get(
            "first_air_date"
        ),

        "fecha_final": data.get(
            "last_air_date"
        ),

        "estado": data.get(
            "status"
        ),

        "rating": data.get(
            "vote_average"
        ),

        "numero_temporadas": data.get(
            "number_of_seasons"
        ),

        "numero_episodios": data.get(
            "number_of_episodes"
        ),

        "generos": [

            genero["name"]

            for genero in data.get(
                "genres",
                []
            )
        ],

        "idiomas": data.get(
            "languages",
            []
        ),

        "paises": data.get(
            "origin_country",
            []
        ),

        "productoras": [

            empresa["name"]

            for empresa in data.get(
                "production_companies",
                []
            )
        ],

        "temporadas": [

            {
                "temporada":
                temporada["season_number"],

                "nombre":
                temporada["name"],

                "episodios":
                temporada["episode_count"],

                "descripcion":
                temporada["overview"]
            }

            for temporada in data.get(
                "seasons",
                []
            )

            if temporada["season_number"] != 0
        ]
    }

    return limpio


if __name__ == "__main__":

    serie = "Shingeki no Kyojin"

    resultado = buscar_serie(serie)

    if resultado and resultado["results"]:

        tv_id = resultado["results"][0]["id"]

        detalles = obtener_detalles(
            tv_id
        )

        informacion_limpia = sanitizar_tmdb(
            detalles
        )

        print(
            json.dumps(
                informacion_limpia,
                indent=4,
                ensure_ascii=False
            )
        )

        personajes = obtener_personajes(
            tv_id
        )

        print(
            f"Total personajes: {len(personajes)}"
        )

        for personaje in personajes:

            print(personaje)
