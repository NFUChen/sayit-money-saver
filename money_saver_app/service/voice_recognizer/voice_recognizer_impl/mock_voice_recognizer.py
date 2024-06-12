from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer


class MockVoiceRecognizer(VoiceRecognizer):
    """
    A mock implementation of the `VoiceRecognizer` interface, used for testing purposes.
    """

    def __init__(self, text: str) -> None:
        self.text = text

    def recognize(self, voice_bytes: bytes) -> str:
        return self.text
