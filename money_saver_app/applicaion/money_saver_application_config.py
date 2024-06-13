from dataclasses import dataclass
from enum import Enum

from application.application_config import BaseApplicationConifig
from money_saver_app.service.voice_recognizer.voice_recognizer_impl.openai_whisper_voice_recognizer import (
    OpenAIWhisperConfig,
)


class ApplicationMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


@dataclass
class MoneySaverApplicationConfig:
    base_config: BaseApplicationConifig
    sql_url: str
    mode: ApplicationMode
    openai_whisper_config: OpenAIWhisperConfig
