from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from .vector_store import (
    obtener_vector_store
)


def recuperar_contexto(query, limite=4):

    store = obtener_vector_store(
        "series_db"
    )

    resultados = store.similarity_search(
        query,
        k=limite
    )

    return "\n\n".join(
        [doc.page_content for doc in resultados]
    )


def recuperar_opiniones(query, limite=3):

    store = obtener_vector_store(
        "opiniones_db"
    )

    resultados = store.similarity_search(
        query,
        k=limite
    )

    return "\n".join(
        [doc.page_content for doc in resultados]
    )


def recuperar_memoria(query, limite=2):

    store = obtener_vector_store(
        "memoria_usuario"
    )

    resultados = store.similarity_search(
        query,
        k=limite
    )

    return "\n".join(
        [doc.page_content for doc in resultados]
    )


def construir_prompt(contexto, opiniones, memoria, pregunta):

    return (
        "Eres un asistente experto en series y anime. "
        "Usa el contexto para responder con recomendaciones claras.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Opiniones relevantes:\n{opiniones}\n\n"
        f"Memoria del usuario:\n{memoria}\n\n"
        f"Pregunta del usuario:\n{pregunta}"
    )


def responder(llm, pregunta):

    contexto = recuperar_contexto(
        pregunta
    )

    opiniones = recuperar_opiniones(
        pregunta
    )

    memoria = recuperar_memoria(
        pregunta
    )

    prompt = construir_prompt(
        contexto,
        opiniones,
        memoria,
        pregunta
    )

    mensajes = [
        SystemMessage(
            content="Eres un asistente local especializado en series."
        ),
        HumanMessage(
            content=prompt
        )
    ]

    return llm.invoke(
        mensajes
    )
