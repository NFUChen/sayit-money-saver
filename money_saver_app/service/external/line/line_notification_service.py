from typing import Callable, Iterable
import schedule
from linebot import LineBotApi
from money_saver_app.repository.models import Platform, User
from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.user_service import UserService

class LineNotificationService:
    def __init__(self, 
                 line_push_api: LineBotApi, 
                 user_service: UserService, 
                 transaction_service: TransactionService
        ) -> None:
        self.transaction_service = transaction_service
        self.user_service = user_service
        self.api = line_push_api
        
    def __schedule_auto_push_notification(self, jobs: Iterable[Callable]) -> None:
        for job in jobs:
            schedule.every().day.at("03:59").do(job)
        
        
    @property
    def all_users(self) -> Iterable[User]:
        return self.user_service.get_all_users_on_platform(Platform.LINE)
        