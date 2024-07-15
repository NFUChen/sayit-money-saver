import datetime
from threading import Thread
import time
from typing import Callable
from loguru import logger
import schedule
from linebot import LineBotApi
from money_saver_app.repository.models import Platform, UserRead
from money_saver_app.service.external.line.line_models import (
    LineTextSendMessage,
    UserProfile,
)
from money_saver_app.service.money_saver.transaction_service import (
    TransactionService,
    TransactionSet,
)
from money_saver_app.service.money_saver.user_service import UserService


class LineNotificationService:
    def __init__(
        self,
        line_push_api: LineBotApi,
        user_service: UserService,
        transaction_service: TransactionService,
    ) -> None:
        self.transaction_service = transaction_service
        self.user_service = user_service
        self.api = line_push_api

    def schedule_auto_push_notification(self) -> None:
        jobs: list[Callable] = [self._notify_all_users_with_self_transactions]
        for job in jobs:
            logger.info(f"[JOB SCHEDULING] Scheduling job: {job.__name__}")
            schedule.every().day.at("23:55", "UTC").do(job)

        def wrapper() -> None:
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        Thread(target=wrapper).start()

    def _format_transaction_set(
        self, transaction_set: TransactionSet
    ) -> LineTextSendMessage:
        items_repr = [
            f"[{transaction.recorded_date} | {transaction.item.item_category}] {transaction.item.name}: {transaction.amount}"
            for transaction in transaction_set.transactions
        ]
        set_expense = f"總花費: {transaction_set.grouped_transactions.expense.total_amount}"
        return LineTextSendMessage("\n".join([*items_repr, set_expense]))

    def _notify_all_users_with_self_transactions(self) -> None:
        logger.info("[JOB] Running job: _notify_all_users_with_self_transactions")

        end_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            hours=8
        )
        start_date = end_date - datetime.timedelta(days=1)

        for user in self.all_target_users:
            transaction_set = self.transaction_service.get_all_transactions_by_user_id_within_date_range(
                user.id,
                start_date,
                end_date,
            )
            logger.debug(f"[JOB] User: {user.id} has {len(transaction_set.transactions)} transactions")
            if transaction_set.is_empty_set:
                continue
            user_profile = UserProfile.model_validate_json(
                self.api.get_profile(user.external_id).as_json_string()
            )
            self.api.push_message(
                user.external_id, self._format_transaction_set(transaction_set)
            )

    @property
    def all_target_users(self) -> list[UserRead]:
        return self.user_service.get_all_users_on_platform(Platform.LINE)
