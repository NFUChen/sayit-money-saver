import datetime
from re import T
from typing import Optional

from sqlmodel import select, col


from money_saver_app.repository.models import Transaction, TransactionItem, User
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository


class UserRepository(SQLCrudRepository[int, User]):
    def find_user_by_email(self, email: str) -> Optional[User]:
        return self._find_by(select(User).where(User.email == email))

    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self._find_by(select(User).where(User.user_name == user_name))


class TransactionRepository(SQLCrudRepository[int, Transaction]):
    def find_all_transactions_by_user_id(
        self, id: int, limit: int
    ) -> list[Transaction]:
        return self._find_all_by(
            select(Transaction)
            .where(Transaction.user_id == id)
            .order_by(col(Transaction.created_at).desc())
            .limit(limit)
        )[::-1]

    def find_all_transactions_by_user_id_within_date_range(
        self, id: int, start_date: datetime.date, end_date: datetime.date
    ) -> list[Transaction]:
        return self._find_all_by(
            select(Transaction)
            .where(Transaction.user_id == id)
            .where(
                Transaction.created_at > start_date, Transaction.created_at < end_date
            )
            .order_by(col(Transaction.created_at).asc())
        )


class TransactionItemRepository(SQLCrudRepository[int, TransactionItem]): ...
