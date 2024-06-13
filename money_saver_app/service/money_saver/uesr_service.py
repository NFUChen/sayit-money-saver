from typing import Optional
from money_saver_app.repository.models import User
from money_saver_app.repository.recorder_repository import (
    UserRepository,
    UserTokenRepository,
)


class UserService:
    def __init__(
        self, user_repo: UserRepository, user_token_repo: UserTokenRepository
    ) -> None:
        self.user_repo = user_repo
        self.user_token_repo = user_token_repo

    def save_user(self, user: User) -> None:
        self.user_repo.save(user)

    def get_user_id_by_token(self, token: str) -> Optional[int]:
        return self.user_token_repo.get_uesr_id_by_token(token)
