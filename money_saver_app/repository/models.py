import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, func
from sqlmodel import Column, Field, Relationship, SQLModel


class TransactionType(str, Enum):
    Revenue = "Revenue"
    Expense = "Expense"


class Role(str, Enum):
    Admin = "Admin"
    User = "User"
    Guest = "Guest"
    BlockedUser = "BlockedUser"


class User(SQLModel, table=True):
    __tablename__: str = "user"
    user_name: str
    email: str = Field(unique=True)
    hashed_password: str = Field(exclude=True)
    transactions: list["Transaction"] = Relationship(back_populates="user")
    id: int | None = Field(default=None, primary_key=True)
    role: Role


class TransactionItem(SQLModel, table=True):
    __tablename__: str = "transaction_item"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    item_category: str
    transaction: "Transaction" = Relationship(back_populates="item")

    updated_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(), onupdate=func.now())
    )


class Transaction(SQLModel, table=True):
    __tablename__: str = "transaction"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    transaction_type: TransactionType = Field(index=True)
    amount: int

    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    user: User = Relationship(back_populates="transactions")

    item_id: UUID | None = Field(default=None, foreign_key="transaction_item.id")
    item: TransactionItem = Relationship(back_populates="transaction")

    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: datetime.datetime | None = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        sa_column=Column(DateTime(), onupdate=func.now()),
    )

    __table_args__ = (
        CheckConstraint(Column("amount") >= 0, name="amount_non_negative"),
    )
