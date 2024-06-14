from enum import Enum


class TransactionType(str, Enum):
    Revenue = "Revenue"
    Expense = "Expense"