from money_saver_app.repository.models import Transaction, User, TransactionItem
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository


class UserRepository(SQLCrudRepository[int, User]): ...


class TransactionRepository(SQLCrudRepository[int, Transaction]): ...
    
class TransactionItemRepository(SQLCrudRepository[int, TransactionItem]): ...
    