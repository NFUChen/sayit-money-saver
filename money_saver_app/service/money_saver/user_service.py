from typing import Optional, cast

from loguru import logger
from openai import BaseModel
from passlib.context import CryptContext
from sqlalchemy import Engine
from sqlmodel import Session

from money_saver_app.repository.models import (
    ExternalUser,
    Platform,
    Role,
    User,
    UserRead,
)
from money_saver_app.repository.recorder_repository import (
    ExternalUserRepository,
    UserRepository,
)
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
        self,
        sql_engine: Engine,
        user_repo: UserRepository,
        external_uesr_repo: ExternalUserRepository,
        password_context: CryptContext,
    ) -> None:
        self.engine = sql_engine
        self.password_context = password_context
        self.user_repo = user_repo
        self.external_uesr_repo = external_uesr_repo

    def get_user_role_by_id(self, id: int) -> Role:
        optional_user = self.get_user_by_id(id)
        if optional_user is None:
            raise UserNotFoundError(user_id=id)

        return optional_user.role

    def is_user_a_role_type_by_id(self, id: int, role: Role) -> bool:
        return role == self.get_user_role_by_id(id)

    def is_user_exist_by_email(self, email: str) -> bool:
        return self.user_repo.find_user_by_email(email) is not None

    def register_user(self, guest: Guest) -> UserRead:
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

        return saved_user.as_read()

    def register_line_user(self, line_id: str) -> UserRead:
        optional_external_user = (
            self.external_uesr_repo.find_user_by_external_id_on_platform(
                Platform.LINE, line_id
            )
        )
        if optional_external_user is not None:
            logger.info(
                f"[LINE USER] Line user already registered: {optional_external_user.external_id}, skipping registration"
            )

            optional_user = self.user_repo.find_by_id(
                cast(int, optional_external_user.user_id)
            )
            if optional_user is None:
                raise UserNotFoundError(user_id=optional_external_user.user_id)
            return optional_user.as_read()

        with Session(self.engine, expire_on_commit=False) as session:
            user = User(user_name="", email="", hashed_password="", role=Role.Guest)
            external_user = ExternalUser(
                user=user, external_id=line_id, platform=Platform.LINE
            )
            session.add(user)
            session.add(external_user)
            session.commit()
            logger.info(
                f"[NEW LINE USER] New line user registered: {external_user.external_id}"
            )
            session.refresh(user)
            return user.as_read()

    def save_user(self, user: User) -> None:
        self.user_repo.save(user)

    def get_user_by_email(self, email: str) -> Optional[UserRead]:
        optional_user = self.user_repo.find_user_by_email(email)
        if optional_user is None:
            return
        return optional_user.as_read()

    def get_user_by_user_name(self, user_name: str) -> Optional[UserRead]:
        optional_user = self.user_repo.find_user_by_user_name(user_name)
        if optional_user is None:
            return
        return optional_user.as_read()

    def get_user_by_id(self, id: int) -> Optional[UserRead]:
        optional_user = self.user_repo.find_by_id(id)
        if optional_user is None:
            return
        return optional_user.as_read()

    def get_all_users(self) -> list[UserRead]:
        return [user.as_read() for user in self.user_repo.find_all()]

    def get_all_users_on_platform(self, platform: Platform) -> list[UserRead]:
        return [
            external_user.user.as_read()
            for external_user in self.external_uesr_repo.find_all_users_on_platform(
                platform
            )
        ]

    def __get_hashed_password(self, raw_password: str) -> str:
        return self.password_context.hash(raw_password)
