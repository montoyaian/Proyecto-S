from concurrent.futures import ThreadPoolExecutor
import time

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from .vector_store import (
    obtener_vector_store
)


def recuperar_contexto(query, limite=2, serie_id=None):
    store = obtener_vector_store("series_db")
    filtro = {"id": serie_id} if serie_id else None
    resultados = store.similarity_search(query, k=limite, filter=filtro)
    return "\n\n".join([doc.page_content for doc in resultados])


def recuperar_opiniones(query, limite=2, serie_id=None):
    store = obtener_vector_store("opiniones_db")
    filtro = {"serie_id": serie_id} if serie_id else None
    resultados = store.similarity_search(query, k=limite, filter=filtro)
    return "\n".join([doc.page_content for doc in resultados])


def recuperar_memoria(query, limite=2, serie_id=None):
    store = obtener_vector_store("memoria_usuario")
    resultados = store.similarity_search(query, k=limite)
    return "\n".join([doc.page_content for doc in resultados])


def truncar_fragmento(texto, max_caracteres=300):
    if not texto:
        return ""
    texto = " ".join(texto.split())
    if len(texto) <= max_caracteres:
        return texto
    return texto[:max_caracteres].rstrip() + "..."


def construir_prompt(contexto, opiniones, memoria, pregunta):
    contexto = "\n\n".join(truncar_fragmento(f) for f in contexto.split("\n\n") if f.strip())
    opiniones = "\n".join(truncar_fragmento(f) for f in opiniones.split("\n") if f.strip())
    memoria = "\n".join(truncar_fragmento(f) for f in memoria.split("\n") if f.strip())
    return (
        "Eres un asistente experto en series y anime. "
        "Usa el contexto para responder con recomendaciones claras.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Opiniones relevantes:\n{opiniones}\n\n"
        f"Memoria del usuario:\n{memoria}\n\n"
        f"Pregunta del usuario:\n{pregunta}"
    )


def responder(llm, pregunta, on_chunk=None, serie_id=None):
    with ThreadPoolExecutor(max_workers=3) as executor:
        contexto_fut = executor.submit(recuperar_contexto, pregunta, serie_id=serie_id)
        opiniones_fut = executor.submit(recuperar_opiniones, pregunta, serie_id=serie_id)
        memoria_fut = executor.submit(recuperar_memoria, pregunta, serie_id=serie_id)
        contexto = contexto_fut.result()
        opiniones = opiniones_fut.result()
        memoria = memoria_fut.result()
    prompt = construir_prompt(contexto, opiniones, memoria, pregunta)
    mensajes = [
        SystemMessage(content="Eres un asistente local especializado en series."),
        HumanMessage(content=prompt)
    ]
    if on_chunk:
        partes = []
        for chunk in llm.stream(mensajes):
            contenido = getattr(chunk, "text", None)
            if contenido is None:
                contenido = getattr(chunk, "content", "") or ""
                if isinstance(contenido, list):
                    contenido = "".join(item.get("text", "") for item in contenido if isinstance(item, dict))
            if contenido:
                on_chunk(contenido)
                partes.append(contenido)
        return "".join(partes)
    else:
        respuesta = llm.invoke(mensajes)
        return getattr(respuesta, "content", "") or ""