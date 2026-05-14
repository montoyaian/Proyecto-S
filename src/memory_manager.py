from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from .vector_store import (
    obtener_vector_store
)


def construir_prompt_memoria(historial):

    return (
        "Extrae preferencias del usuario de la conversacion. "
        "Solo devuelve JSON con campos: tipo y contenido. "
        "Si no hay informacion relevante, devuelve {}.\n\n"
        f"Conversacion:\n{historial}"
    )


def guardar_memoria(llm, historial):

    prompt = construir_prompt_memoria(
        historial
    )

    mensajes = [
        SystemMessage(
            content="Eres un extractor de preferencias."
        ),
        HumanMessage(
            content=prompt
        )
    ]

    respuesta = llm.invoke(
        mensajes
    )

    contenido = respuesta.content.strip()

    if contenido == "{}" or not contenido:
        return None

    store = obtener_vector_store(
        "memoria_usuario"
    )

    store.add_texts(
        texts=[contenido],
        metadatas=[{"tipo": "preferencia"}]
    )

    store.persist()

    return contenido
