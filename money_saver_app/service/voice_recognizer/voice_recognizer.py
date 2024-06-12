from abc import ABC, abstractmethod


class VoiceRecognizer(ABC):
    """
    Defines an abstract base class for voice recognition services.
    The `VoiceRecognizer` class provides an abstract interface for recognizing speech from audio input and returning the recognized text as a string. 
    Concrete subclasses must implement the `recognize()` method to provide the actual voice recognition functionality.
    """
    @abstractmethod
    def recognize(self, voice_bytes: bytes) -> str: ...
        

