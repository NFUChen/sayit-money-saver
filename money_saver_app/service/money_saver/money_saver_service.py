from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.user_service import UserService
from money_saver_app.service.pipeline_service.pipeline_impls.pipeline_factory import (
    TextPipelineFactory,
    VoicePipelineFactory,
)
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    MoneySaverPipelineContext,
    VoicePipelineContext,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase


class MoneySaverService:
    """
    Provides the main service for the Money Saver application, which executes the voice pipeline to process user voice input and perform money saving actions.
    The MoneySaverService class is responsible for orchestrating the various services and components required to execute the voice pipeline, including the voice recognizer, transaction service, and large language model.
    The `execute_pipeline` method is the main entry point for processing user voice input.
    It creates a `VoicePipelineContext` object with the necessary dependencies, and then executes the pipeline steps defined by the `VoicePipelineFactory`.
    """

    def __init__(
        self,
        engine: Engine,
        voice_pipeline_factory: VoicePipelineFactory,
        text_pipeline_factory: TextPipelineFactory,
        user_service: UserService,
        transaction_service: TransactionService,
        model_llm: LargeLanguageModelBase,
        voice_recognizer: VoiceRecognizer,
    ) -> None:
        self.engine = engine
        self.voice_pipeline_factory = voice_pipeline_factory
        self.text_pipeline_factory = text_pipeline_factory
        self.user_service = user_service
        self.transaction_service = transaction_service
        self.llm = model_llm
        self.voice_recognizer = voice_recognizer

    def execute_voice_pipeline(
        self, voice_bytes: bytes, user_id: int
    ) -> VoicePipelineContext:
        with Session(self.engine) as session:
            context = VoicePipelineContext(
                voice_bytes=voice_bytes,
                session=session,
                user_id=user_id,
                voice_recognizer=self.voice_recognizer,
                transaction_service=self.transaction_service,
                llm=self.llm,
            )
            steps = self.voice_pipeline_factory.create_pipeline(context)
            for step in steps:
                step.execute()
        return context

    def execute_text_pipeline(
        self, source_text: str, user_id: int
    ) -> MoneySaverPipelineContext:
        with Session(self.engine) as session:
            context = MoneySaverPipelineContext(
                session=session,
                user_id=user_id,
                transaction_service=self.transaction_service,
                llm=self.llm,
                source_text=source_text,
            )
            steps = self.text_pipeline_factory.create_pipeline(context)
            for step in steps:
                step.execute()
        return context
