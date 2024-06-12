from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer


class OpenAIWhiswerVoiceRecognizer(VoiceRecognizer):
    def recognize(self) -> str: ...
