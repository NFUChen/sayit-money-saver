from abc import abstractmethod
from typing import Iterable

from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.uesr_service import UserService
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    StepTextToTransactionView,
    StepTransactionVivePersitence,
    StepVoiceParsing,
    VoicePipelineContext,
)
from money_saver_app.service.pipeline_service.pipeline_step import (
    PipelineContext,
    PipelineStep,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase


class PipelineFactory:
    @abstractmethod
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]: ...


class VoicePipelineFactory(PipelineFactory): ...


class VoiceProductionPipelineFactory(VoicePipelineFactory):
    """
    The `VoiceProductionPipelineFactory` class is responsible for creating a pipeline of steps for processing voice input in a production environment.
    The pipeline includes the following steps:
    1. `StepVoiceParsing`: Parses the voice input using the provided `VoiceRecognizer`.
    2. `StepTextToTransactionView`: Converts the parsed text into a transaction view using the provided `LargeLanguageModelBase`.
    3. `StepTransactionVivePersitence`: Persists the transaction view using the provided `TransactionService`.

    The factory is initialized with the necessary dependencies, including `UserService`, `TransactionService`, `LargeLanguageModelBase`, and `VoiceRecognizer`.
    """

    def __init__(
        self,
        user_service: UserService,
        transaction_service: TransactionService,
        model_llm: LargeLanguageModelBase,
        voice_recognizer: VoiceRecognizer,
    ) -> None:
        self.user_service = user_service
        self.transaction_service = transaction_service
        self.llm = model_llm
        self.voice_recognizer = voice_recognizer

    def create_pipeline(self, context: VoicePipelineContext) -> Iterable[PipelineStep]:
        return [
            StepVoiceParsing(context, self.voice_recognizer),
            StepTextToTransactionView(context, self.llm),
            StepTransactionVivePersitence(context, self.transaction_service),
        ]


class VoiceDevelopmentPipelineFactory(VoicePipelineFactory):
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]:
        return []
