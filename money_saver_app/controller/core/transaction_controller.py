from typing import Iterable
from fastapi import APIRouter, Depends
from loguru import logger
from money_saver_app.controller.core.depends_utils import get_current_user_id
from money_saver_app.controller.core.route_controller import RouterController
from money_saver_app.repository.models import TransactionRead
from money_saver_app.service.money_saver.transaction_service import TransactionService


class TransactionController(RouterController):
    def __init__(
        self, router_prefix: str, transaction_service: TransactionService
    ) -> None:
        self.router_prefix = router_prefix
        self.transaction_service = transaction_service

    def register_routes(self) -> APIRouter:
        router = APIRouter(prefix=self.router_prefix)

        @router.get("/transactions")
        def get_all_transaction_by_user_id(
            user_id: int = Depends(get_current_user_id),
        ) -> Iterable[TransactionRead]:
            logger.info(user_id)
            return [
                model.as_read()
                for model in self.transaction_service.get_all_transaction_by_user_id(
                    user_id
                )
            ]

        return router
