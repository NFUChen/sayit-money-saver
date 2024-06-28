import datetime
from fastapi import APIRouter, Depends
from loguru import logger
from money_saver_app.controller.core.depends_utils import get_current_user_id
from money_saver_app.controller.core.router_controller import RouterController
from money_saver_app.service.money_saver.transaction_service import (
    TransactionService,
    TransactionSet,
)


class TransactionController(RouterController):
    def __init__(
        self, router_prefix: str, transaction_service: TransactionService
    ) -> None:
        self.router_prefix = router_prefix
        self.transaction_service = transaction_service

    def register_routes(self) -> APIRouter:
        router = APIRouter(prefix=self.router_prefix)

        @router.get("/transactions")
        def get_all_transactions_by_user_id(
            limit: int = 50, user_id: int = Depends(get_current_user_id)
        ) -> TransactionSet:
            logger.info(user_id)
            return self.transaction_service.get_all_transactions_by_user_id(
                user_id, limit
            )

        @router.get("/transactions/date-range")
        def get_all_transactions_by_user_id_within_date_range(
            start_date: datetime.date,
            end_date: datetime.date,
            user_id: int = Depends(get_current_user_id),
        ) -> TransactionSet:
            logger.info(user_id)
            return self.transaction_service.get_all_transactions_by_user_id_within_date_range(
                user_id, start_date=start_date, end_date=end_date
            )

        return router
