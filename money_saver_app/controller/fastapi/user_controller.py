from typing import Iterable

from fastapi import APIRouter, FastAPI
from loguru import logger
from money_saver_app.controller.fastapi.route_controller import RouterController
from money_saver_app.repository.models import User
from money_saver_app.service.money_saver.error_code import UserNotFoundError
from money_saver_app.service.money_saver.uesr_service import Guest, UserService


class UesrController(RouterController):
    def __init__(self, user_service: UserService, route_prefix: str) -> None:
        self.api_router = APIRouter(prefix=route_prefix)
        self.user_service = user_service

    def register_routes(self, app: FastAPI) -> None:
        @self.api_router.get("/users")
        def get_all_uesrs() -> Iterable[User]:
            return self.user_service.get_all_users()

        @self.api_router.post("/users")
        def register_user(user: Guest) -> User:
            registerd_user = self.user_service.register_user(user)
            logger.info(f"register_user: {user}")

            return registerd_user

        app.include_router(self.api_router)
