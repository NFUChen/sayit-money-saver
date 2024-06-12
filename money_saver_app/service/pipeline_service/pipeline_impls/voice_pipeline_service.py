from money_saver_app.service.pipeline_service.pipeline_executor import PipelineExecutor
from money_saver_app.service.pipeline_service.pipeline_impls.pipeline_factory import (
    PipelineFactory,
)
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    VoicePipelineContext,
)


class VoicePipelineExecutor(PipelineExecutor):
    def __init__(
        self,
        pipeline_factory: PipelineFactory,
    ) -> None:
        self.pipeline_factory = pipeline_factory

    def execute(self, context: VoicePipelineContext) -> bool:
        steps = self.pipeline_factory.create_pipeline(context)
        for step in steps:
            step.execute()
        return True
