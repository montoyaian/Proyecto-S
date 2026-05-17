from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from .config import (
    EMBEDDING_MODEL,
    CHROMA_DIR
)


_EMBEDDINGS = None
_STORES = {}


def crear_embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _EMBEDDINGS


def obtener_vector_store(nombre_coleccion):
    if nombre_coleccion in _STORES:
        return _STORES[nombre_coleccion]
    embeddings = crear_embeddings()
    store = Chroma(
        collection_name=nombre_coleccion,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    _STORES[nombre_coleccion] = store
    return store


def almacenar_documento(nombre_coleccion, documento, metadata=None):
    if not documento:
        return
    store = obtener_vector_store(nombre_coleccion)
    store.add_texts(
        texts=[documento["texto"]],
        metadatas=[metadata or {}],
        ids=[documento["id"]]
    )
    store.persist()


def almacenar_textos(nombre_coleccion, textos, metadatas=None, ids=None):
    if not textos:
        return
    store = obtener_vector_store(nombre_coleccion)
    store.add_texts(texts=textos, metadatas=metadatas, ids=ids)
    store.persist()


def _armar_resultado(resultados):
    if not resultados:
        return None
    ids = resultados.get("ids") or []
    documentos = resultados.get("documents") or []
    metadatas = resultados.get("metadatas") or []
    if not ids:
        return None
    return {
        "id": ids[0],
        "texto": documentos[0] if documentos else "",
        "metadata": metadatas[0] if metadatas else {}
    }


def buscar_documento_por_titulo(nombre_coleccion, titulo, titulo_normalizado):
    store = obtener_vector_store(nombre_coleccion)
    if titulo_normalizado:
        resultados = store.get(where={"titulo_norm": titulo_normalizado}, include=["metadatas", "documents"])
        existente = _armar_resultado(resultados)
        if existente:
            return existente
    if titulo:
        resultados = store.get(where={"titulo": titulo}, include=["metadatas", "documents"])
        existente = _armar_resultado(resultados)
        if existente:
            return existente
    resultados = store.get(include=["metadatas", "documents"])
    ids = resultados.get("ids") or []
    documentos = resultados.get("documents") or []
    metadatas = resultados.get("metadatas") or []
    for indice, meta in enumerate(metadatas):
        titulo_meta = (meta or {}).get("titulo", "")
        titulo_meta_norm = (meta or {}).get("titulo_norm", "")
        if titulo_meta_norm and titulo_meta_norm == titulo_normalizado:
            return {"id": ids[indice], "texto": documentos[indice] if documentos else "", "metadata": meta or {}}
        if titulo_meta and titulo_meta.strip().lower() == titulo_normalizado:
            return {"id": ids[indice], "texto": documentos[indice] if documentos else "", "metadata": meta or {}}
    return None