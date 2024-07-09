import copy
from datetime import datetime, timedelta, timezone
from typing import Optional, TypedDict

import jwt
from loguru import logger
from passlib.context import CryptContext

from money_saver_app.repository.models import UserRead
from money_saver_app.service.money_saver.error_code import (
    PasswordNotMatchError,
    UserNotFoundError,
)
from money_saver_app.service.money_saver.user_service import UserService


class JwtConfig(TypedDict):
    secret_key: str
    access_token_expire_minutes: int


JsonWebToken = str


class JWTUser(TypedDict):
    id: int


class AuthService:
    """
    The `AuthService` class provides authentication-related functionality for the Money Saver application.

    It includes methods for:
    - Verifying a user's password against a hashed password
    - Generating a JSON Web Token (JWT) for a user based on their user data
    - Logging in a user by their username or email, and returning a JWT
    The class requires a `UserService` instance, a `CryptContext` for password hashing/verification, and a `JwtConfig` dictionary with the JWT secret key and access token expiration time.
    """

    def __init__(
        self,
        user_service: UserService,
        password_context: CryptContext,
        jwt_config: JwtConfig,
    ) -> None:
        self.jwt_config = jwt_config
        self.user_service = user_service
        self.password_context = password_context
        self.secret_key = self.jwt_config["secret_key"]
        self.jwt_algorithm = "HS256"

    def get_jwt_user_from_jwt(self, token: str) -> Optional[JWTUser]:
        """
        Validates a JSON Web Token (JWT) by decoding it using the configured secret key and algorithm.

        Args:
            token (str): The JWT token to validate.
        """
        try:
            jwt_user: JWTUser = jwt.decode(
                token, self.secret_key, algorithms=[self.jwt_algorithm]
            )
            user_id = jwt_user["id"]
            optional_user = self.user_service.get_user_by_id(user_id)
            if optional_user is None:
                raise UserNotFoundError(user_id=user_id)

        except jwt.exceptions.InvalidTokenError as invalid_token_error:
            logger.exception(invalid_token_error)
            return

        return jwt_user

    def __is_verified_password(self, raw_password: str, hashed_password: str) -> bool:
        return self.password_context.verify(raw_password, hashed_password)

    def __get_payload_jwt(self, payload: dict) -> JsonWebToken:
        payload_copy = copy.deepcopy(payload.copy())
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.jwt_config["access_token_expire_minutes"]
        )
        payload_copy.update({"exp": expire})
        return jwt.encode(payload_copy, self.secret_key, algorithm=self.jwt_algorithm)

    def __user_login_base_func(
        self, optiona_user: Optional[UserRead], input_password: str
    ) -> JsonWebToken:
        if optiona_user is None:
            raise UserNotFoundError()

        is_verfied = self.__is_verified_password(
            input_password, optiona_user.hashed_password
        )
        if not is_verfied:
            raise PasswordNotMatchError()
        return self.__get_payload_jwt(optiona_user.model_dump())

    def user_login_by_user_name(
        self, user_name: str, input_password: str
    ) -> JsonWebToken:
        optional_user = self.user_service.get_user_by_user_name(user_name)
        return self.__user_login_base_func(optional_user, input_password)

    def user_login_by_email(self, email: str, input_password: str) -> JsonWebToken:
        optiona_user = self.user_service.get_user_by_email(email)
        return self.__user_login_base_func(optiona_user, input_password)
