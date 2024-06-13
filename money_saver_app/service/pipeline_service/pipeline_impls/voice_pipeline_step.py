from typing import Optional, cast

from pydantic import Field
from sqlmodel import Session

from money_saver_app.service.money_saver.error_code import (
    OptionalTextMissingError,
    TokenNotFoundError,
    TransactionViewNotFoundError,
)
from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.uesr_service import UserService
from money_saver_app.service.money_saver.views import TransactionView
from money_saver_app.service.pipeline_service.pipeline_step import (
    PipelineContext,
    PipelineStep,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase


class VoicePipelineContext(PipelineContext):
    """
    Represents the context for a voice pipeline step in the money saver application.

    Attributes:
        voice_bytes (bytes): The bytes of the voice data.
        session (Session): The SQLModel session for the database.
        user_id (Optional[int]): The optional user ID associated with the voice data.
        transcribed_text (Optional[str]): The optional transcribed text from the voice data.
    """

    voice_bytes: bytes = Field(exclude=True)
    session: Session = Field(exclude=True)
    token: str

    view: Optional[TransactionView] = None
    user_id: Optional[int] = 1
    transcribed_text: Optional[str] = None
    is_saved: bool = False


class StepTokenSeachUser(PipelineStep):
    """
    Represents a pipeline step that searches for a user by token.
    """

    def __init__(
        self, context: VoicePipelineContext, user_service: UserService
    ) -> None:
        self.context = context
        self.user_service = user_service

    def execute(self) -> None:
        optional_user_id = self.user_service.get_user_id_by_token(self.context.token)

        optional_user_id = self.user_service.get_user_id_by_token(self.context.token)
        if optional_user_id is None:
            raise TokenNotFoundError(self.context.token)

        self.context.user_id = optional_user_id


class StepVoiceParsing(PipelineStep):
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

    def __init__(
        self, context: VoicePipelineContext, voice_recognizer: VoiceRecognizer
    ) -> None:
        self.context = context
        self.voice_recognizer = voice_recognizer

    def execute(self) -> None:
        voice_bytes = self.context.voice_bytes
        text = self.voice_recognizer.recognize(voice_bytes)
        self.context.transcribed_text = text


class StepTextToTransactionView(PipelineStep):
    """
    Represents a pipeline step that converts the transcribed voice data into a transaction view.

    This step takes the transcribed text from the `VoicePipelineContext` and uses a `LargeLanguageModelBase` to generate a `TransactionView` object.
    The generated `TransactionView` is then stored in the `VoicePipelineContext` for use in subsequent pipeline steps.

    Args:
        context (VoicePipelineContext): The context for the voice pipeline step.
        model_llm (LargeLanguageModelBase): The large language model to use for generating the transaction view.

    Raises:
        None
    """

    def __init__(
        self, context: VoicePipelineContext, model_llm: LargeLanguageModelBase
    ) -> None:
        self.context = context
        self.model_llm = model_llm

    def execute(self) -> None:
        optional_text = self.context.transcribed_text
        if optional_text is None:
            raise OptionalTextMissingError()

        optional_view = TransactionView.model_ask(optional_text, self.model_llm)
        if optional_view is None:
            raise TransactionViewNotFoundError(optional_text)

        self.context.view = optional_view


class StepTransactionVivePersitence(PipelineStep):
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

    def __init__(
        self, context: VoicePipelineContext, transaction_service: TransactionService
    ) -> None:
        self.context = context
        self.transaction_service = transaction_service

    def execute(self) -> None:
        optional_view = self.context.view
        if optional_view is None:
            raise TransactionViewNotFoundError()

        is_saved = self.transaction_service.save_transaction_view(
            cast(int, self.context.user_id), optional_view
        )

        self.context.is_saved = is_saved
