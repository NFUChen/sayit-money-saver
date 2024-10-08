import datetime
from typing import Any, Iterable, Optional
from uuid import UUID


from pydantic import BaseModel, Field, computed_field
from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.repository.models import (
    Transaction,
    TransactionItem,
    TransactionRead,
)
from money_saver_app.repository.recorder_repository import (
    TransactionRepository,
    UserRepository,
)
from money_saver_app.service.money_saver.error_code import UserNotFoundError
from money_saver_app.service.money_saver.view_model_common import TransactionType
from money_saver_app.service.money_saver.views import TransactionView


class _GroupItem(BaseModel):
    name: str
    amount: int


class _Group(BaseModel):
    items: list[_GroupItem]


    @computed_field
    @property
    def total_amount(self) -> int:
        return sum([item.amount for item in self.items])


class _GroupedTransaction(BaseModel):
    expense: _Group
    income: _Group



class TransactionSet(BaseModel):
    transactions: list[TransactionRead]

    private_balance: int = Field(default=0, exclude=True)
    private_grouped_transactions: _GroupedTransaction = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:

        expense_group = _Group(items=[])
        income_group = _Group(items=[])
        
        for transaction in self.transactions:
            group_item = _GroupItem(name=transaction.item.name, amount=transaction.amount)
            match transaction.transaction_type:
                case TransactionType.Expense:
                    expense_group.items.append(group_item)
                    self.private_balance -= transaction.amount
                    
                case TransactionType.Income:
                    income_group.items.append(group_item)
                    self.private_balance += transaction.amount

        self.private_grouped_transactions =_GroupedTransaction(expense= expense_group, income=income_group)

    @property
    def is_empty_set(self) -> bool:
        return len(self.transactions) == 0

    @computed_field
    @property
    def number_of_transactions(self) -> int:
        return len(self.transactions)

    @computed_field
    @property
    def balance(self) -> int:
        return self.private_balance

    @computed_field
    @property
    def grouped_transactions(self) -> _GroupedTransaction:
        return self.private_grouped_transactions


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

    def save_transaction_view(
        self, user_id: int, view: TransactionView
    ) -> Optional[TransactionRead]:
        with Session(self.engine) as session:
            user = self.user_repo.find_by_id(user_id, session)
            if user is None:
                raise UserNotFoundError(user_id)
            item = TransactionItem(
                name=view.item.name,
                description=view.item.description,
                item_category=view.item.item_category,
            )
            transaction = Transaction(
                transaction_type=view.transaction_type,
                amount=view.amount,
                user=user,
                item=item,
            )

            session.add(transaction)
            session.commit()
            session.refresh(transaction)

            return transaction.as_read()

    def _convert_to_transaction_set(
        self, transactions: Iterable[Transaction]
    ) -> TransactionSet:
        return TransactionSet(
            transactions=[_model.as_read() for _model in transactions]
        )

    def get_all_transactions_by_user_id_within_date_range(
        self, user_id: int, start_date: datetime.date, end_date: datetime.date
    ) -> TransactionSet:
        return self._convert_to_transaction_set(
            self.transaction_repo.find_all_transactions_by_user_id_within_date_range(
                user_id, start_date, end_date
            )
        )

    def get_all_transactions_by_user_id(self, id: int, limit: int) -> TransactionSet:
        return self._convert_to_transaction_set(
            self.transaction_repo.find_all_transactions_by_user_id(id, limit)
        )

    def get_transaction_by_id(self, id: UUID) -> Optional[TransactionRead]:
        optional_transaction = self.transaction_repo.find_by_id(id)
        if optional_transaction is None:
            return
        return optional_transaction.as_read()

    def delete_transaction_by_id(self, id: UUID) -> bool:
        return self.transaction_repo.delete_by_id(id)
