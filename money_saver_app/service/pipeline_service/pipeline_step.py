from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel


class PipelineContext(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    ...


C = TypeVar("C", bound=PipelineContext)


class PipelineStep(ABC, Generic[C]):
    """
    Defines the base class for a pipeline step in the application's data processing pipeline.

    A pipeline step is an abstract class that must be implemented by concrete pipeline steps.
    Each pipeline step is responsible for validating the context of the pipeline and executing
    a specific data processing task within the overall pipeline.
    """

    def __init__(self, context: C) -> None: ...

    def execute(self) -> None:
        """
        Executes the data processing task defined by the concrete pipeline step implementation.

        This method should contain the core logic for the pipeline step, validating the pipeline context
        and performing the necessary data processing operations.
        """
        ...
