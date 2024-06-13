from typing import Iterable, Optional

from loguru import logger
from openai import BaseModel

from money_saver_app.repository.models import User
from money_saver_app.repository.recorder_repository import (
    UserRepository,
    UserTokenRepository,
)


class Guest(BaseModel):
    user_name: str
    email: str
    password: str


class UserService:
    def __init__(
        self, user_repo: UserRepository, user_token_repo: UserTokenRepository
    ) -> None:
        self.user_repo = user_repo
        self.user_token_repo = user_token_repo

    def register_user(self, new_user: Guest) -> User:
        user = User(
            user_name=new_user.user_name,
            email=new_user.email,
            hashed_password="hashed_password",
            is_active=False,
        )
        saved_user = self.user_repo.save(user)

        return saved_user

    def save_user(self, user: User) -> None:
        self.user_repo.save(user)

    def get_user_id_by_token(self, token: str) -> Optional[int]:
        return self.user_token_repo.get_uesr_id_by_token(token)

    def get_all_users(self) -> Iterable[User]:
        return self.user_repo.find_all()
