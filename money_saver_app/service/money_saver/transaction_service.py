from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.repository.models import Transaction
from money_saver_app.repository.recorder_repository import (
    TransactionRepository,
    UserRepository,
)
from money_saver_app.service.money_saver.error_code import UserNotFoundError
from money_saver_app.service.money_saver.views import TransactionView


class TransactionService:
    """
    Provides a service for saving transactions for a user.

    The `TransactionService` class is responsible for managing the creation and persistence of transactions for a user. It interacts with the `UserRepository` and `TransactionRepository` to handle the underlying data storage and retrieval.

    Args:
        sql_engine (Engine): The SQLAlchemy engine used for database connections.
        user_repo (UserRepository): The repository for managing user data.
        transaction_repo (TransactionRepository): The repository for managing transaction data.

    Raises:
        UserNotFoundError: If the user associated with the transaction is not found.

    Returns:
        bool: True if the transaction was successfully saved, False otherwise.
    """

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
