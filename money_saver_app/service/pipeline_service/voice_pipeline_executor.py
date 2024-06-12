from money_saver_app.service.money_saver.money_saver_service import MoneySaverService
from money_saver_app.service.pipeline_service.pipeline_steps.pipeline_step import (
    PipelineStep,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from money_saver_app.service.pipeline_service.pipeline_steps.voice_pipeline_step import (
    StepTokenSeachUser,
    StepVoiceParsing,
    StepTextToTransactionView,
    StepTransactionVivePersitence,
    VoicePipelineContext,
)
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase


class VoicePipelineExecutor:
    """
    The `VoicePipelineExecutor` class is responsible for executing a pipeline of steps to process voice input and save transactions.
    
    The class takes in a `MoneySaverService`, `VoiceRecognizer`, and `LargeLanguageModelBase` instance, which are used by the pipeline steps to perform their respective tasks.
    
    The `execute` method runs the pipeline by creating a list of `PipelineStep` instances and calling the `execute` method on each one. The pipeline steps include:
    - `StepTokenSeachUser`: Searches for the user associated with the voice input.
    - `StepVoiceParsing`: Parses the voice input to extract relevant information.
    - `StepTextToTransactionView`: Converts the parsed voice input into a transaction view.
    - `StepTransactionVivePersitence`: Persists the transaction view to the money saver service.
    
    The method returns `True` if the pipeline execution is successful
    """
    def __init__(
        self,
        money_saver_service: MoneySaverService,
        voice_recognizer: VoiceRecognizer,
        llm: LargeLanguageModelBase,
    ) -> None:
        self.money_saver_service = money_saver_service
        self.voice_recognizer = voice_recognizer
        self.model_llm = llm

    def execute(self, context: VoicePipelineContext) -> bool:
        pipelinee_steps: list[PipelineStep] = [
            StepTokenSeachUser(context, self.money_saver_service),
            StepVoiceParsing(context, self.voice_recognizer),
            StepTextToTransactionView(context, self.model_llm),
            StepTransactionVivePersitence(context, self.money_saver_service),
        ]
        for step in pipelinee_steps:
            step.execute()

        return True
