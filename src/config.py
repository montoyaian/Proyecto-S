import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)


def get_env(name, default=None):

    value = os.getenv(name)

    if value is None:
        return default

    return value


TMDB_API_KEY = get_env(
    "TMDB_API_KEY"
)

TRAKT_CLIENT_ID = get_env(
    "TRAKT_CLIENT_ID"
)

OLLAMA_BASE_URL = get_env(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = get_env(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

EMBEDDING_MODEL = get_env(
    "EMBEDDING_MODEL",
    "intfloat/multilingual-e5-base"
)

CHROMA_DIR = get_env(
    "CHROMA_DIR",
    os.path.join(
        BASE_DIR,
        "data",
        "chroma"
    )
)

DOCUMENT_CACHE = get_env(
    "DOCUMENT_CACHE",
    os.path.join(
        BASE_DIR,
        "data",
        "documentos.json"
    )
)
