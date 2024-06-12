from abc import abstractmethod
from typing import Iterable
from money_saver_app.service.money_saver.money_saver_service import MoneySaverService
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


class VoiceProductionPipelineFactory(PipelineFactory):
    def __init__(
        self,
        money_saver_service: MoneySaverService,
        model_llm: LargeLanguageModelBase,
        voice_recognizer: VoiceRecognizer,
    ) -> None:
        self.money_saver_service = money_saver_service
        self.llm = model_llm
        self.voice_recognizer = voice_recognizer

    def create_pipeline(self, context: VoicePipelineContext) -> Iterable[PipelineStep]:
        return [
            StepTokenSeachUser(context, self.money_saver_service),
            StepVoiceParsing(context, self.voice_recognizer),
            StepTextToTransactionView(context, self.llm),
            StepTransactionVivePersitence(context, self.money_saver_service),
        ]


class VoiceDevelopmentPipelineFactory(PipelineFactory):
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]:
        return []
