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
    """
    Provides a service for executing a pipeline of voice processing steps.

    The `MoneySaverService` class is responsible for managing the execution of a voice processing pipeline. It takes an SQLAlchemy engine and a pipeline factory as dependencies, and provides a method to execute the pipeline with a given voice data and token.

    The `execute_pipeline` method creates a `VoicePipelineContext` with the provided voice data, session, and token, and then uses the pipeline factory to create the pipeline steps. It then executes each step in the pipeline.

    Args:
        engine (Engine): The SQLAlchemy engine to use for database connections.
        voice_pipeline_factory (VoicePipelineFactory | VoiceDevelopmentPipelineFactory): The factory to use for creating the voice processing pipeline.

    Returns:
        bool: True if the pipeline execution was successful, False otherwise.
    """

    def __init__(
        self,
        engine: Engine,
        voice_pipeline_factory: VoicePipelineFactory,
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
