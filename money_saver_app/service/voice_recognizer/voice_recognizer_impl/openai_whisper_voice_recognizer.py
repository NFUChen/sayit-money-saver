import io
import os
import uuid
from typing import TypedDict, cast

import whisper
from loguru import logger
from pydub import AudioSegment

from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer


class OpenAIWhisperConfig(TypedDict):
    model_name: str


class OpenAIWhisperVoiceRecognizer(VoiceRecognizer):
    def __init__(self, model_config: OpenAIWhisperConfig) -> None:
        self.model = whisper.load_model(model_config["model_name"])

    def recognize(self, audio_bytes: bytes) -> str:
        file_name = self.__create_temp_file(audio_bytes)
        result = self.model.transcribe(file_name)
        text = cast(str, result["text"])
        self.__delete_temp_file(file_name)
        return text

    def __create_temp_file(self, audio_bytes: bytes) -> str:
        audio: AudioSegment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        temp_file_name = f"{uuid.uuid4()}.wav"
        audio.export(temp_file_name, format="wav")
        logger.info(f"[AUDIO EXPORT] Export audio bytes to: {temp_file_name}")
        return temp_file_name

    def __delete_temp_file(self, file_path: str) -> None:
        if os.path.exists(file_path):
            logger.info(f"[FILE REMOVAL] Remove temp file: {file_path}")
            os.remove(file_path)
