from recorder_app.repository.models import Transaction, User, TransactionItem
from recorder_app.repository.sql_crud_repository import SQLCrudRepository


class UserRepository(SQLCrudRepository[int,User]):
    ...

class TransactionRepository(SQLCrudRepository[int,Transaction]):
    ...

class TransactionItemRepository(SQLCrudRepository[int,TransactionItem]):
    ...