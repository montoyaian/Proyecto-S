from concurrent.futures import ThreadPoolExecutor
import time

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from .vector_store import (
    obtener_vector_store
)


def recuperar_contexto(query, limite=2):

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


def recuperar_opiniones(query, limite=2):

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


def truncar_fragmento(texto, max_caracteres=300):

    if not texto:
        return ""

    texto = " ".join(texto.split())

    if len(texto) <= max_caracteres:
        return texto

    return texto[:max_caracteres].rstrip() + "..."


def construir_prompt(contexto, opiniones, memoria, pregunta):
    contexto = "\n\n".join(
        truncar_fragmento(fragmento)
        for fragmento in contexto.split("\n\n")
        if fragmento.strip()
    )

    opiniones = "\n".join(
        truncar_fragmento(fragmento)
        for fragmento in opiniones.split("\n")
        if fragmento.strip()
    )

    memoria = "\n".join(
        truncar_fragmento(fragmento)
        for fragmento in memoria.split("\n")
        if fragmento.strip()
    )

    return (
        "Eres un asistente experto en series y anime. "
        "Usa el contexto para responder con recomendaciones claras.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Opiniones relevantes:\n{opiniones}\n\n"
        f"Memoria del usuario:\n{memoria}\n\n"
        f"Pregunta del usuario:\n{pregunta}"
    )


def responder(llm, pregunta, on_chunk=None):
    inicio_total = time.perf_counter()

    def _medir(nombre, funcion, *args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        print(f"[timing] {nombre}: {duracion:.3f}s")
        return resultado

    with ThreadPoolExecutor(max_workers=3) as executor:
        contexto_fut = executor.submit(
            _medir,
            "recuperar_contexto",
            recuperar_contexto,
            pregunta
        )
        opiniones_fut = executor.submit(
            _medir,
            "recuperar_opiniones",
            recuperar_opiniones,
            pregunta
        )
        memoria_fut = executor.submit(
            _medir,
            "recuperar_memoria",
            recuperar_memoria,
            pregunta
        )

        contexto = contexto_fut.result()
        opiniones = opiniones_fut.result()
        memoria = memoria_fut.result()

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

    inicio_llm = time.perf_counter()

    if on_chunk:
        partes = []
        for chunk in llm.stream(mensajes):
            contenido = getattr(chunk, "content", "") or ""
            if contenido:
                on_chunk(contenido)
                partes.append(contenido)
        contenido = "".join(partes)
    else:
        respuesta = llm.invoke(
            mensajes
        )
        contenido = getattr(respuesta, "content", "") or ""

    duracion_llm = time.perf_counter() - inicio_llm
    duracion_total = time.perf_counter() - inicio_total
    print(f"[timing] llm.invoke: {duracion_llm:.3f}s")
    print(f"[timing] total_respuesta: {duracion_total:.3f}s")

    return contenido
