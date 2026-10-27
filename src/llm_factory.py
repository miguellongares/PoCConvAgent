from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled

from config import settings

set_tracing_disabled(True)  # built-in tracing sends data to OpenAI's platform


def make_model() -> OpenAIChatCompletionsModel:
    """Return the configured model client. Change .env to swap models."""
    client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)
    return OpenAIChatCompletionsModel(model=settings.llm_model, openai_client=client)
