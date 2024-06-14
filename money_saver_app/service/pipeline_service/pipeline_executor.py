from money_saver_app.service.pipeline_service.pipeline_step import PipelineContext


class PipelineExecutor:
    """
    Executes a pipeline.

    Returns:
        bool: True if the pipeline execution was successful, False otherwise.
    """

    def execute(self, context: PipelineContext) -> bool: ...
