import datetime
from typing import Callable, cast
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
        jobs: list[Callable] = [self.schedule_auto_push_notification]
        for job in jobs:
            logger.info(f"[JOB SCHEDULING] Scheduling job: {job.__name__}")
            schedule.every().day.at("23:59").do(job)

        schedule.run_pending()

    def _format_transaction_set(
        self, transaction_set: TransactionSet
    ) -> LineTextSendMessage:
        items_repr = [
            f"[{transaction.recorded_date} | {transaction.item.item_category}] {transaction.item.name}: {transaction.amount}"
            for transaction in transaction_set.transactions
        ]
        transaction_balance = f"Balance: {transaction_set.balance}"
        return LineTextSendMessage("\n".join([*items_repr, transaction_balance]))

    def _notify_all_users_with_self_transactions(self) -> None:
        start_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            hours=8
        )
        end_date = start_date + datetime.timedelta(days=1)

        for user in self.all_target_users:
            transaction_set = self.transaction_service.get_all_transactions_by_user_id_within_date_range(
                user.id,
                start_date,
                end_date,
            )
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
