from typing import Iterable, Optional

from loguru import logger
from openai import BaseModel
from passlib.context import CryptContext

from money_saver_app.repository.models import Role, User
from money_saver_app.repository.recorder_repository import UserRepository
from money_saver_app.service.money_saver.error_code import (
    EmailDuplicationError,
    UserNotFoundError,
)


class Guest(BaseModel):
    """
    A data model representing a guest user, with fields for user name, email, and password.
    This model is used to capture the necessary information for registering a new user.
    """

    user_name: str
    email: str
    password: str


class UserService:
    """
    Provides a service layer for managing user-related operations, including user registration, saving user data, and retrieving user information by email, username, or token.

    The `UserService` class is responsible for handling user-related business logic, such as hashing passwords, saving user data, and retrieving user information from the underlying repository.

    Args:
        user_repo (UserRepository): A repository for managing user data.
        user_token_repo (UserTokenRepository): A repository for managing user tokens.
        password_context (CryptContext): A context for hashing and verifying passwords.

    Attributes:
        password_context (CryptContext): The password hashing and verification context.
        user_repo (UserRepository): The repository for managing user data.
    """

    def __init__(
        self, user_repo: UserRepository, password_context: CryptContext
    ) -> None:
        self.password_context = password_context
        self.user_repo = user_repo

    def get_user_role_by_id(self, id: int) -> Role:
        optional_user = self.get_user_by_id(id)
        if optional_user is None:
            raise UserNotFoundError(user_id=id)

        return optional_user.role

    def is_user_a_role_type_by_id(self, id: int, role: Role) -> bool:
        return role == self.get_user_role_by_id(id)

    def is_user_exist_by_email(self, email: str) -> bool:
        return self.user_repo.find_user_by_email(email) is not None

    def register_user(self, guest: Guest) -> User:
        if self.is_user_exist_by_email(guest.email):
            raise EmailDuplicationError()

        user = User(
            user_name=guest.user_name,
            email=guest.email,
            hashed_password=self.__get_hashed_password(guest.password),
            role=Role.Guest,
        )
        saved_user = self.user_repo.save(user)
        logger.info(f"[NEW USER] New user registered: {saved_user.user_name}")

        return saved_user

    def save_user(self, user: User) -> None:
        self.user_repo.save(user)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.find_user_by_email(email)

    def get_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self.user_repo.find_user_by_user_name(user_name)

    def get_user_by_id(self, id: int) -> Optional[User]:
        return self.user_repo.find_by_id(id)

    def get_all_users(self) -> Iterable[User]:
        return self.user_repo.find_all()

    def __get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)
