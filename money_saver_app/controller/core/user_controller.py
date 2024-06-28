from typing import Iterable

from fastapi import APIRouter, Depends
from loguru import logger

from money_saver_app.controller.core.depends_utils import get_current_user_id
from money_saver_app.controller.core.router_controller import RouterController
from money_saver_app.repository.models import User
from money_saver_app.service.money_saver.user_service import UserService


class UserController(RouterController):
    def __init__(self, router_prefix: str, user_service: UserService) -> None:
        self.router_prefix = router_prefix
        self.user_service = user_service

    def register_routes(self) -> APIRouter:
        router = APIRouter(prefix=self.router_prefix)

        @router.get("/users")
        def get_all_users(
            user_id: int = Depends(get_current_user_id),
        ) -> Iterable[User]:
            logger.info(user_id)
            return self.user_service.get_all_users()

        return router
