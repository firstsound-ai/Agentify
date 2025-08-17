from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from settings import settings


def get_llm_model(
    temperature: float = 0.5,
    model_name: Optional[str] = None,
    model_kwargs: Optional[dict] = None,
) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=settings.OPENAI_API_BASE,
        api_key=SecretStr(settings.OPENAI_API_KEY),
        model=model_name if model_name else settings.DEFAULT_MODEL,
        temperature=temperature,
        model_kwargs=model_kwargs or {},
    )
