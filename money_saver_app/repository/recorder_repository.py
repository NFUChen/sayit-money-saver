import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import col, select

from money_saver_app.repository.models import (
    ExternalUser,
    Platform,
    Transaction,
    TransactionItem,
    User,
)
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository


class ExternalUserRepository(SQLCrudRepository[int, ExternalUser]):
    def find_user_by_external_id_on_platform(
        self, platform: Platform, external_id: str
    ) -> Optional[ExternalUser]:
        optional_external_user = self._find_by(
            select(ExternalUser).where(
                ExternalUser.external_id == external_id,
                ExternalUser.platform == platform,
            )
        )
        if optional_external_user is None:
            return
        return optional_external_user

    def find_all_users_on_platform(self, platform: Platform) -> list[ExternalUser]:
        if platform == Platform.Self:
            raise ValueError(
                "[INVALID PLATFORM] Platform cannot be self, fectching from UserRepository instead."
            )

        return [
            external_user
            for external_user in self._find_all_by(
                select(ExternalUser).where(ExternalUser.platform == platform)
            )
        ]


class UserRepository(SQLCrudRepository[int, User]):
    def find_user_by_email(self, email: str) -> Optional[User]:
        return self._find_by(select(User).where(User.email == email))

    def find_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self._find_by(select(User).where(User.user_name == user_name))


class TransactionRepository(SQLCrudRepository[UUID, Transaction]):
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
                Transaction.recorded_date > start_date, Transaction.recorded_date < end_date
            )
            .order_by(col(Transaction.created_at).asc())
        )


class TransactionItemRepository(SQLCrudRepository[int, TransactionItem]): ...
