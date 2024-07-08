from enum import Enum
from typing import Union
from typing_extensions import Self

from pydantic import Field, model_validator

from money_saver_app.service.money_saver.view_model_common import ExpenseCategory, IncomeCategory, TransactionType
from smart_base_model.core.smart_base_model.smart_base_model import SmartBaseModel


class AssistantActionType(Enum):
    """
    Defines the different types of actions that an assistant can perform.

    Actions:
        - `AddTransaction`: Represents the action of adding a new transaction, either an expense or revenue. 
        Patterns such as: 
            - "Add a <amount> expense for <item name>"
            - "<item name> <amount>"
        - `Reporting`: Represents the action of generating various reports. This could include a summary of transactions, 
        a detailed transaction history, or records for a specific period.
        Examples: 
            - "Show me the transaction history for last month."
            - "I want to see the records of a certain day."

        - `Unclear`: Represents the scenario where the assistant is unable to determine the user's intent due to lack of context, 
        ambiguity, or unrecognizable transaction details.
        Examples: 
            - "What's up?" -> This is the scenario where the assistant is unable to determine the user's intent due to lack of context.
            - "book" -> This is the scenario where the assistant is unable to determine the user's intent due to ambiguity and lack of transaction details (i.e., the amount).
    **IMPORTANT**
      - Use `Unclear` action with caution; only use it if you genuinely cannot understand what the user is asking for.
      - If an item name with amount is specified (e.g., '<item name> <amount>'), please use the `AddTransaction` action instead.
    """
    AddTransaction = "AddTransaction"
    Reporting = "Reporting"
    Unclear = "Unclear"


class AssistantActionView(SmartBaseModel["AssistantActionView"]):
    """
    Represents an action that can be performed by an assistant.

    The `action_type` field specifies the type of action
    """

    action_type: AssistantActionType


class TransactionItemView(SmartBaseModel["TransactionItemView"]):
    """
    Represents a view model for a transaction item, containing information about the item associated with a transaction.

    "The `name` field contains the name of the item. Please correct any typos found here."
    The `description` field holds a description of the item.
    The `item_category` field holds the category of the item, please select based on provided enum values.
    """

    name: str
    description: str
    item_category: Union[ExpenseCategory, IncomeCategory]


class TransactionView(SmartBaseModel["TransactionView"]):
    """
    Represents a view model for a transaction, containing information about the transaction type, amount, and associated item.

    The `transaction_type` field holds the type of the transaction, which can be one of the values defined in the `TransactionType` enum.
    The `amount` field holds the amount of the transaction.
    The `item` field holds a `TransactionItemView` object representing the item associated with the transaction.

    Note:
     - This model is used within the context of a money saver app, where most transactions are categorized as expenses （成本, 費用）.
     - However, there are exceptions for income transactions, such as bank savings (銀行儲蓄、個人儲蓄、銀行存款、個人存款、活期、活期儲蓄存) and personal savings etc.
     - Most of the user of this app is Chinese, so model up the object with value being Traditional Chinese
     - You may receive a item name following an amount representing a trasaction, please refer examples below.
    注意：
        此模型在記帳軟體的基礎下使用，其中大多數交易（成本, 費用）被分類為支出 (Expense)。
        但也有交易列為收入的情況，例如銀行儲蓄、個人儲蓄、銀行存款、個人存款、活期、活期儲蓄存款等、此類狀況下請歸類為 收入 (Revenue)。
        絕大部分軟體使用者為中文使用者, 請使用『繁體中文』建立此物件

    Examples:
        Pattern <item name> <amount>
            - 雞腿便當100 -> 雞腿便當 NT100
            - 牛奶60 -> 牛奶 NT60
    """

    transaction_type: TransactionType
    amount: int = Field(gt=0, default=0)
    item: TransactionItemView


    @model_validator(mode= "after")
    def _valid_transaction_item(self) -> Self:
        match self.transaction_type.value:
            case TransactionType.Expense.value:
                if isinstance(self.item.item_category, IncomeCategory):
                    raise ValueError(f"The transaction type is {self.transaction_type}, but the item category is {self.item.item_category}")
            case TransactionType.Income.value:
                if isinstance(self.item.item_category, ExpenseCategory):
                    raise ValueError(f"The transaction type is {self.transaction_type}, but the item category is {self.item.item_category}")
        
        return self

