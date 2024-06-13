from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from loguru import logger
import uvicorn
from money_saver_app.applicaion.money_saver_application import MoneySaverController
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from money_saver_app.controller.fastapi.middlewares.exception_middleware import (
    ExceptionMiddleware,
)
from money_saver_app.controller.fastapi.route_controller import RouterController
from money_saver_app.controller.fastapi.user_controller import UesrController


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
    - Registering the `UesrController` with the `/api/admin` prefix.

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

        self.app.middleware("http")(ExceptionMiddleware())

    def register_routes(self) -> None:
        @self.app.get("/")
        def read_root():
            return {"message": "Welcome to Money Saver API"}

        self.route_controllers: Iterable[RouterController] = [
            UesrController(self.user_service, "/api/admin")
        ]

        for controller in self.route_controllers:
            controller.register_routes(self.app)

    def run(self) -> None:
        uvicorn.run(self.app, host="0.0.0.0", port=8000)
