from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.service.pipeline_service.pipeline_impls.pipeline_factory import (
    VoiceDevelopmentPipelineFactory,
    VoicePipelineFactory,
)
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    VoicePipelineContext,
)


class MoneySaverService:
    def __init__(
        self,
        engine: Engine,
        voice_pipeline_factory: VoicePipelineFactory | VoiceDevelopmentPipelineFactory,
    ) -> None:
        self.engine = engine
        self.factory = voice_pipeline_factory

    def execute_pipeline(self, voice_bytes: bytes, token: str) -> bool:
        with Session(self.engine) as session:
            context = VoicePipelineContext(
                voice_bytes=voice_bytes, session=session, token=token
            )
            steps = self.factory.create_pipeline(context)
            for step in steps:
                step.execute()

        return True
