from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from .config import (
    EMBEDDING_MODEL,
    CHROMA_DIR
)


def crear_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def obtener_vector_store(nombre_coleccion):

    embeddings = crear_embeddings()

    return Chroma(
        collection_name=nombre_coleccion,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )


def almacenar_documento(nombre_coleccion, documento, metadata=None):

    if not documento:
        return

    store = obtener_vector_store(
        nombre_coleccion
    )

    store.add_texts(
        texts=[documento["texto"]],
        metadatas=[metadata or {}],
        ids=[documento["id"]]
    )

    store.persist()


def almacenar_textos(nombre_coleccion, textos, metadatas=None, ids=None):

    if not textos:
        return

    store = obtener_vector_store(
        nombre_coleccion
    )

    store.add_texts(
        texts=textos,
        metadatas=metadatas,
        ids=ids
    )

    store.persist()
