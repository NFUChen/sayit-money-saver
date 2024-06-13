from typing import TypedDict
from typing_extensions import NotRequired

from smart_base_model.llm.llm_impls.ollama_large_language_model import OllamaModelConfig
from smart_base_model.llm.llm_impls.openai_large_language_model import OpenAIModelConfig


class BaseApplicationConifig(TypedDict):
    openai_config: NotRequired[OpenAIModelConfig]
    ollama_config: NotRequired[OllamaModelConfig]
