from dataclasses import dataclass
from typing import Annotated, Iterable

from loguru import logger
from pydantic import BaseModel
import uvicorn
from fastapi import Depends, FastAPI, File
from fastapi.middleware.cors import CORSMiddleware

from money_saver_app.application.money_saver_application import MoneySaverController
from money_saver_app.controller.core.auth_controller import AuthController
from money_saver_app.controller.core.depends_utils import get_current_user_id
from money_saver_app.controller.core.middlewares.auth_middleware import (
    AuthMiddleware,
)
from money_saver_app.controller.core.middlewares.exception_middleware import (
    ExceptionMiddleware,
)
from money_saver_app.controller.core.route_controller import RouterController
from money_saver_app.controller.core.transaction_controller import TransactionController
from money_saver_app.controller.core.user_controller import UserController
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    MoneySaverPipelineContext,
    VoicePipelineContext,
)


class TextPipelineRequest(BaseModel):
    source_text: str


@dataclass
class VoiceMoneySaverWebController(MoneySaverController, RouterController):
    """
    The `VoiceMoneySaverWebController` class is responsible for setting up and running the FastAPI application for the Money Saver API.
    It inherits from `MoneySaverController` and `RouterController` to leverage their functionality.

    The `__post_init__` method is called after the object is initialized, and it performs the following tasks:
    - Creates a FastAPI application instance and assigns it to the `app` attribute.
    - Registers the routes for the application by calling the `register_routes` method.
    - Adds CORS middleware to the application to allow cross-origin requests.
    - Adds an exception middleware to the application to handle exceptions.

    The `register_routes` method sets up the routes for the application, including:
    - A root route that returns a welcome message.
    - Registering the `UserController` with the `/api/admin` prefix.

    The `run` method starts the FastAPI application using the `uvicorn` server, listening on `0.0.0.0:8000`.
    """

    def __post_init__(self) -> None:
        self.app = FastAPI()
        self.register_routes()

        self.app.add_middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.register_middlewares()

    def register_middlewares(self) -> None:
        exclueded_routes = ["/api/public", "/openapi.json", "/docs"]
        middlewares = [
            ExceptionMiddleware(),
            AuthMiddleware(self.auth_service, exclueded_routes),
        ]
        for middleware in middlewares:
            self.app.middleware("http")(middleware)

    def register_routes(self) -> None:
        @self.app.get("/")
        def read_root():
            return {"message": "Welcome to Money Saver API"}

        @self.app.post("/api/save-record-from-audio")
        def save_record_from_audio(
            audio_file: Annotated[bytes, File()],
            current_user_id: int = Depends(get_current_user_id),
        ) -> VoicePipelineContext:
            logger.info(f"[PIPELINE EXECUTION] User ID: {current_user_id}")
            context = self.money_saver_service.execute_voice_pipeline(
                audio_file, current_user_id
            )
            logger.info(f"[PIPELINE FINAL CONTEXT] Context: {context.model_dump()}")
            return context

        @self.app.post("/api/save-record-from-text")
        def save_record_from_text(
            text_pipeline_context: TextPipelineRequest,
            current_user_id: int = Depends(get_current_user_id),
        ) -> MoneySaverPipelineContext:
            logger.info(f"[PIPELINE EXECUTION] User ID: {current_user_id}")
            context = self.money_saver_service.execute_text_pipeline(
                text_pipeline_context.source_text, current_user_id
            )
            logger.info(f"[PIPELINE FINAL CONTEXT] Context: {context.model_dump()}")
            return context

        self.route_controllers: Iterable[RouterController] = [
            AuthController("/api/public/auth", self.auth_service, self.user_service),
            UserController("/api/private/admin", self.user_service),
            TransactionController("/api/private/personal", self.transaction_service),
        ]

        for controller in self.route_controllers:
            router = controller.register_routes()
            self.app.include_router(router)

    def run(self) -> None:
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
