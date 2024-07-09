from dataclasses import dataclass
from enum import Enum

from application.application_config import BaseApplicationConfig
from money_saver_app.service.money_saver.auth_service import JwtConfig
from money_saver_app.service.voice_recognizer.voice_recognizer_impl.openai_whisper_voice_recognizer import (
    OpenAIWhisperConfig,
)


@dataclass
class LineServiceConfig:
    channel_access_token: str
    channel_secret: str


@dataclass
class MoneySaverApplicationConfig:
    base_config: BaseApplicationConfig
    sql_url: str
    openai_whisper_config: OpenAIWhisperConfig
    jwt_config: JwtConfig
    line_service_config: LineServiceConfig
