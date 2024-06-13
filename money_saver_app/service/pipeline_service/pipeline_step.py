from abc import ABC

from pydantic import BaseModel


class PipelineContext(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    ...


class PipelineStep(ABC):
    """
    Defines the base class for a pipeline step in the application's data processing pipeline.

    A pipeline step is an abstract class that must be implemented by concrete pipeline steps.
    Each pipeline step is responsible for validating the context of the pipeline and executing
    a specific data processing task within the overall pipeline.
    """

    def __init__(self, context: PipelineContext) -> None: ...

    def execute(self) -> None:
        """
        Executes the pipeline step, processing the data in the provided pipeline context.

        Args:
            context (PipelineContext): The pipeline context containing the data to be processed.

        Returns:
            PipelineContext: The updated pipeline context after the step has been executed.
        """
        ...
