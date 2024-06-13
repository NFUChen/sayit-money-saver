from typing import Iterable, Optional

from openai import BaseModel

from money_saver_app.repository.models import User
from money_saver_app.repository.recorder_repository import UserRepository
from passlib.context import CryptContext


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

    def register_user(self, guest: Guest) -> User:
        user = User(
            user_name=guest.user_name,
            email=guest.email,
            hashed_password=self.__get_hashed_password(guest.password),
            is_active=False,
        )
        saved_user = self.user_repo.save(user)

        return saved_user

    def save_user(self, user: User) -> None:
        self.user_repo.save(user)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.find_user_by_email(email)

    def get_user_by_user_name(self, user_name: str) -> Optional[User]:
        return self.user_repo.find_user_by_user_name(user_name)

    def get_all_users(self) -> Iterable[User]:
        return self.user_repo.find_all()

    def __get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)
