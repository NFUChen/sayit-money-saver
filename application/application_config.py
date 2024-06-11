from dataclasses import dataclass

from smart_base_model.llm.llm_impls.openai_large_language_model import OpenAIModelConfig


@dataclass
class BaseApplicationConifig:
    openai_config: OpenAIModelConfig
