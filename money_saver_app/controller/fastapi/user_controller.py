from typing import Iterable

from fastapi import APIRouter

from money_saver_app.controller.fastapi.route_controller import RouterController
from money_saver_app.repository.models import User
from money_saver_app.service.money_saver.user_service import UserService


class UesrController(RouterController):
    def __init__(self, router_prefix: str, user_service: UserService) -> None:
        self.router_prefix = router_prefix
        self.user_service = user_service

    def register_routes(self) -> APIRouter:
        router = APIRouter(prefix=self.router_prefix)

        @router.get("/users")
        def get_all_uesrs() -> Iterable[User]:
            return self.user_service.get_all_users()

        return router
