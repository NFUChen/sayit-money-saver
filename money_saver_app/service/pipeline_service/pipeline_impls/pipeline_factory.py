from abc import abstractmethod
from typing import Iterable

from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    MoneySaverPipelineContext,
    StepTextToTransactionView,
    StepTransactionVivePersistence,
    StepVoiceParsing,
    VoicePipelineContext,
)
from money_saver_app.service.pipeline_service.pipeline_step import (
    PipelineContext,
    PipelineStep,
)


class PipelineFactory:
    @abstractmethod
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]: ...


class VoicePipelineFactory(PipelineFactory):
    def create_pipeline(self, context: VoicePipelineContext) -> Iterable[PipelineStep]:
        return [
            StepVoiceParsing(context),
            StepTextToTransactionView(context),
            StepTransactionVivePersistence(context),
        ]


class TextPipelineFactory(PipelineFactory):
    def create_pipeline(
        self, context: MoneySaverPipelineContext
    ) -> Iterable[PipelineStep]:
        return [
            StepTextToTransactionView(context),
            StepTransactionVivePersistence(context),
        ]


class VoiceDevelopmentPipelineFactory(PipelineFactory):
    def create_pipeline(self, context: PipelineContext) -> Iterable[PipelineStep]:
        return []
