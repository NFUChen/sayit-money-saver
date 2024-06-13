from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.repository.models import Transaction
from money_saver_app.repository.recorder_repository import (
    TransactionRepository,
    UserRepository,
)
from money_saver_app.service.money_saver.views import TransactionView
from money_saver_app.service.money_saver.error_code import UserNotFoundError


class TransactionService:
    def __init__(
        self,
        sql_engine: Engine,
        user_repo: UserRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self.engine = sql_engine
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    def save_transaction_view(self, user_id: int, view: TransactionView) -> bool:
        with Session(self.engine) as session:
            user = self.user_repo.find_by_id(user_id, session)
            if user is None:
                raise UserNotFoundError(user_id)

            transaction = Transaction(
                transaction_type=view.transaction_type, amount=view.amount, user=user
            )
            self.transaction_repo.save(transaction, session, is_commit=False)
            session.commit()

        return True
