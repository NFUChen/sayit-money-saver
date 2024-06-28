from enum import Enum

from pydantic import Field


from money_saver_app.service.money_saver.view_model_common import TransactionType
from smart_base_model.core.smart_base_model.smart_base_model import SmartBaseModel


class AssistantActionType(Enum):
    """
    Represents the different types of actions that an assistant can perform.

    - `AddTransaction`: Used to add a new transaction for a record of expense/revenue. For example, "Add a $50 expense for groceries."
    - `Reporting`: Used to generate reports, such as a summary of a collection of transactions or the history of transactions. For example, "Show me the transaction history for last month"
       or "I want to see the records of a certain day".

    Please classify actions accurately based on these definitions.
    """

    AddTransaction = "add_transaction"
    Reporting = "reporting"


class AssistantActionView(SmartBaseModel["AssistantActionView"]):
    """
    Represents an action that can be performed by an assistant.

    The `action_type` field specifies the type of action
    """

    action_type: AssistantActionType


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
     - Most of the user of this app is Chinese, so model up the object with value being Traditional Chinese
    注意：
        此模型在記帳軟體的基礎下使用，其中大多數交易（成本, 費用）被分類為支出 (Expense)。
        但也有交易列為收入的情況，例如銀行儲蓄、個人儲蓄、銀行存款、個人存款、活期、活期儲蓄存款等、此類狀況下請歸類為 收入 (Revenue)。
        絕大部分軟體使用者為中文使用者, 請使用『繁體中文』建立此物件
    """

    transaction_type: TransactionType
    amount: int = Field(gt=0, default=0)
    item: TransactionItemView
