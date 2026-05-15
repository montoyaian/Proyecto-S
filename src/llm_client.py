from langchain_community.chat_models import ChatOllama

from .config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)


def crear_llm():

    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        streaming=True
    )
