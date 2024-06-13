from typing import Literal

from pydantic import Field
from money_saver_app.repository.models import Transaction, TransactionType
from smart_base_model.core.smart_base_model.smart_base_model import SmartBaseModel


class AssistantAction(SmartBaseModel["AssistantAction"]):
    """
    Represents an action that can be performed by an assistant.

    The `action` field specifies the type of action, which can be either "recording" or "reporting".
    """

    action: Literal["recording", "reporting"]


class TransactionItemView(SmartBaseModel["TransactionItemView"]):
    """
    Represents a view model for a transaction item, containing information about the item associated with a transaction.

    The `name` field holds the name of the item.
    The `description` field holds a description of the item.
    The `item_category` field holds the category of the item.
    """

    name: str
    description: str
    item_category: str


class TransactionView(SmartBaseModel["TransactionView"]):
    """
    Represents a view model for a transaction, containing information about the transaction type, amount, and associated item.

    The `transaction_type` field holds the type of the transaction, which can be one of the values defined in the `TransactionType` enum.
    The `amount` field holds the amount of the transaction.
    The `item` field holds a `TransactionItemView` object representing the item associated with the transaction.

    Note:
     - This model is used within the context of a money saver app, where most transactions are categorized as expenses （成本, 費用）.
     - However, there are exceptions for revenue transactions, such as bank savings (銀行儲蓄、個人儲蓄、銀行存款、個人存款、活期、活期儲蓄存) and personal savings etc.

    注意：
        此模型在記帳軟體的基礎下使用，其中大多數交易（成本, 費用）被分類為支出 (Expense)。
        但也有交易列為收入的情況，例如銀行儲蓄、個人儲蓄、銀行存款、個人存款、活期、活期儲蓄存款等、此類狀況下請歸類為 收入 (Revenue)。
        絕大部分使用者為中文使用者, 請使用『繁體中文』回答
    """

    transaction_type: TransactionType
    amount: int = Field(gt=0)
    item: TransactionItemView
