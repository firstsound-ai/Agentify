from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from settings import settings


def get_llm_model(
    temperature: float = 0.5, model_kwargs: Optional[dict] = None
) -> ChatOpenAI:
    if model_kwargs is None:
        model_kwargs = {}
    return ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        base_url=settings.OPENAI_API_BASE,
        api_key=SecretStr(settings.OPENAI_API_KEY),
        temperature=temperature,
        model_kwargs=model_kwargs,
    )
