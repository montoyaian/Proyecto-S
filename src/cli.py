import json

from .data_fetcher import (
    obtener_datos_serie
)

from .document_builder import (
    construir_documento_serie
)

from .vector_store import (
    almacenar_documento,
    almacenar_textos,
    buscar_documento_por_titulo
)

from .llm_client import (
    crear_llm
)

from .rag_system import (
    responder
)

from .memory_manager import (
    guardar_memoria
)

from .config import (
    DOCUMENT_CACHE
)


def normalizar_titulo(texto):

    if not texto:
        return ""

    return " ".join(
        texto.strip().lower().split()
    )


def guardar_documento_cache(doc):

    if not doc:
        return

    registros = []

    try:
        with open(
            DOCUMENT_CACHE,
            "r",
            encoding="utf-8"
        ) as archivo:
            registros = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        registros = []

    registros.append(doc)

    with open(
        DOCUMENT_CACHE,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            registros,
            archivo,
            ensure_ascii=False,
            indent=2
        )


def registrar_serie(nombre):
    titulo_norm = normalizar_titulo(
        nombre
    )

    existente = buscar_documento_por_titulo(
        "series_db",
        nombre,
        titulo_norm
    )

    if existente:
        print("Serie ya registrada. Usando datos locales.")
        return existente

    datos = obtener_datos_serie(
        nombre
    )

    if not datos:
        print("No se encontro la serie.")
        return None

    documento = construir_documento_serie(
        datos
    )

    if not documento:
        print("No se pudo construir el documento.")
        return None

    almacenar_documento(
        "series_db",
        documento,
        metadata={
            "id": documento["id"],
            "titulo": datos.get("tmdb", {}).get("titulo"),
            "titulo_norm": normalizar_titulo(
                datos.get("tmdb", {}).get("titulo")
            ),
            "slug": datos.get("slug")
        }
    )

    comentarios = datos.get("comentarios", [])

    if comentarios:
        textos = [c["comentario"] for c in comentarios]
        ids = [f"{documento['id']}_op_{i}" for i in range(len(comentarios))]
        metadatas = [{"serie_id": documento["id"]} for _ in comentarios]

        almacenar_textos(
            "opiniones_db",
            textos,
            metadatas=metadatas,
            ids=ids
        )

    guardar_documento_cache(
        documento
    )

    return documento


def iniciar_chat():

    llm = crear_llm()

    nombre = input("Serie a consultar: ").strip()

    if not nombre:
        print("Nombre de serie vacio.")
        return

    documento = registrar_serie(
        nombre
    )

    if not documento:
        return

    print("Serie procesada. Puedes preguntar.")

    historial = []

    while True:
        pregunta = input("Tu pregunta: ").strip()

        if pregunta.lower() in {"salir", "exit", "quit"}:
            break

        partes = []

        def _on_chunk(texto):
            print(texto, end="", flush=True)
            partes.append(texto)

        respuesta = responder(
            llm,
            pregunta,
            on_chunk=_on_chunk
        )

        if not partes:
            print(respuesta)
        else:
            print("")

        historial.append(
            f"Usuario: {pregunta}\nAsistente: {respuesta}"
        )

    if historial:
        guardar_memoria(
            llm,
            "\n".join(historial)
        )


if __name__ == "__main__":
    iniciar_chat()
