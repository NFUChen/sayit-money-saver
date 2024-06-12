from typing import Optional
from money_saver_app.repository.models import Transaction, User, TransactionItem
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository


class UserRepository(SQLCrudRepository[int, User]): ...


class TransactionRepository(SQLCrudRepository[int, Transaction]): ...


class TransactionItemRepository(SQLCrudRepository[int, TransactionItem]): ...


class UserTokenRepository:
    def __init__(self) -> None:
        pass

    def get_uesr_id_by_token(self, token: str) -> Optional[int]:
        return 0
