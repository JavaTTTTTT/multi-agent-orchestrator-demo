from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import settings


def get_llm(model: str | None = None, temperature: float = 0) -> ChatOpenAI:
    kwargs = {
        "model": model or settings.HEAVY_MODEL,
        "temperature": temperature,
        "api_key": settings.OPENAI_API_KEY,
    }
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return ChatOpenAI(**kwargs)


def get_light_llm(temperature: float = 0) -> ChatOpenAI:
    return get_llm(model=settings.LIGHT_MODEL, temperature=temperature)


def get_embeddings() -> OpenAIEmbeddings:
    kwargs = {
        "model": settings.EMBEDDING_MODEL,
        "api_key": settings.OPENAI_API_KEY,
    }
    if settings.OPENAI_BASE_URL:
        kwargs["base_url"] = settings.OPENAI_BASE_URL
    return OpenAIEmbeddings(**kwargs)
