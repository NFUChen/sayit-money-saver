from abc import abstractmethod
from typing import Iterable

from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.uesr_service import UserService
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    StepTextToTransactionView,
    StepTokenSeachUser,
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
            StepTokenSeachUser(context, self.user_service),
            StepVoiceParsing(context, self.voice_recognizer),
            StepTextToTransactionView(context, self.llm),
            StepTransactionVivePersitence(context, self.transaction_service),
        ]


class VoiceDevelopmentPipelineFactory(VoicePipelineFactory):
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]:
        return []
