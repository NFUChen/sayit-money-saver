from typing import Optional

from pydantic import Field
from sqlmodel import Session

from money_saver_app.repository.models import TransactionRead
from money_saver_app.service.money_saver.error_code import (
    OptionalTextMissingError,
    TransactionViewNotFoundError,
    UnableToParseViewRequestError,
)
from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.views import TransactionView
from money_saver_app.service.pipeline_service.pipeline_step import (
    PipelineContext,
    PipelineStep,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase


class MoneySaverPipelineContext(PipelineContext):
    """
    Represents the base context for a pipeline step in the money saver application.
    """

    user_id: int
    session: Session = Field(exclude=True)
    llm: LargeLanguageModelBase = Field(exclude=True)
    transaction_service: TransactionService = Field(exclude=True)
    view: Optional[TransactionView] = None
    is_saved: bool = False
    source_text: Optional[str] = None
    transaction_read: Optional[TransactionRead] = Field(default=None, exclude=True)


class VoicePipelineContext(MoneySaverPipelineContext):
    """
    Represents the context for a voice pipeline step in the money saver application.

    Attributes:
        voice_bytes (bytes): The bytes of the voice data.
        session (Session): The SQLModel session for the database.
        user_id (Optional[int]): The optional user ID associated with the voice data.
        source_text (Optional[str]): The optional transcribed text from the voice data.
    """

    voice_bytes: bytes = Field(exclude=True)
    voice_recognizer: VoiceRecognizer = Field(exclude=True)

    def __str__(self) -> str:
        return f"VoicePipelineContext(user_id={self.user_id}, source_text={self.source_text}, is_saved={self.is_saved}, view={self.view}, llm={self.llm.__class__.__name__}, voice_recognizer={self.voice_recognizer.__class__.__name__})"


class StepVoiceParsing(PipelineStep[VoicePipelineContext]):
    """
    Represents a pipeline step that parses voice data and transcribes it to text.

    This step takes the voice data from the `VoicePipelineContext` and uses a `VoiceRecognizer` to transcribe the audio to text.
    The transcribed text is then stored in the `VoicePipelineContext` for use in subsequent pipeline steps.

    Args:
        context (VoicePipelineContext): The context for the voice pipeline step.
        voice_recognizer (VoiceRecognizer): The voice recognizer to use for transcribing the audio.

    Raises:
        None
    """

    def __init__(self, context: VoicePipelineContext) -> None:
        self.context = context
        self.voice_recognizer = context.voice_recognizer

    def execute(self) -> None:
        voice_bytes = self.context.voice_bytes
        text = self.voice_recognizer.recognize(voice_bytes)
        self.context.source_text = text


class StepTextToTransactionView(PipelineStep[MoneySaverPipelineContext]):
    """
    Represents a pipeline step that generates a transaction view from the transcribed voice data.

    This step takes the transcribed text from the `VoicePipelineContext` and uses a large language model (LLM) to generate a `TransactionView` object. The generated `TransactionView` is then stored in the `VoicePipelineContext` for use in subsequent pipeline steps.

    Args:
        context (VoicePipelineContext): The context for the voice pipeline step.
        llm (LargeLanguageModelBase): The large language model to use for generating the transaction view.
    Raises:
        OptionalTextMissingError: If the transcribed text is not available in the context.
        TransactionViewNotFoundError: If the LLM fails to generate a valid transaction view.
    """

    def __init__(self, context: MoneySaverPipelineContext) -> None:
        self.context = context
        self.llm = context.llm

    def execute(self) -> None:
        optional_text = self.context.source_text
        if optional_text is None:
            raise OptionalTextMissingError()

        optional_view = TransactionView.model_ask(optional_text, self.llm)
        if optional_view is None:
            raise UnableToParseViewRequestError(optional_text)

        self.context.view = optional_view


class StepTransactionVivePersistence(PipelineStep[MoneySaverPipelineContext]):
    """
    Represents a pipeline step that persists the transaction view generated from the transcribed voice data.

    This step takes the transaction view from the `VoicePipelineContext` and saves it to the `MoneySaverService`.
    The user ID is retrieved from the token in the context.

    Args:
        context (VoicePipelineContext): The context for the voice pipeline step.
        money_saver_service (MoneySaverService): The service to use for saving the transaction view.

    Raises:
        None
    """

    def __init__(self, context: MoneySaverPipelineContext) -> None:
        self.context = context
        self.transaction_service = context.transaction_service

    def execute(self) -> None:
        optional_view = self.context.view
        if optional_view is None:
            raise TransactionViewNotFoundError()

        transaction_read = self.transaction_service.save_transaction_view(
            self.context.user_id, optional_view
        )

        self.context.is_saved = transaction_read is not None
        self.context.transaction_read = transaction_read
