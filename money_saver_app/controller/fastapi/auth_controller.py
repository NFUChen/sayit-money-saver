from typing import Optional, Union

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from openai import BaseModel

from money_saver_app.controller.fastapi.route_controller import RouterController
from money_saver_app.repository.models import User
from money_saver_app.service.money_saver.auth_service import AuthService
from money_saver_app.service.money_saver.user_service import Guest, UserService


class CredentialContext(BaseModel):
    password: str


class EmailCredential(CredentialContext):
    email: str


class UserNameCredential(CredentialContext):
    user_name: str


CredentialType = Optional[Union[EmailCredential, UserNameCredential]]


class AuthController(RouterController):
    COOKIE_NAME = "jwt"

    def __init__(
        self, route_prefix: str, auth_service: AuthService, user_service: UserService
    ) -> None:
        self.route_prefix = route_prefix
        self.auth_service = auth_service
        self.user_service = user_service

    def register_routes(self) -> APIRouter:
        router = APIRouter(prefix=self.route_prefix)

        @router.post("/login")
        def user_login(
            request: Request, credential: CredentialType = None
        ) -> JSONResponse:
            base_response = JSONResponse("login success")

            if self.__validate_jwt_for_existing_users(request):
                return JSONResponse("already login")
            token = self._handle_token_from_credential(credential)
            base_response.set_cookie(key=self.COOKIE_NAME, value=token, httponly=True)
            return base_response

        @router.post("/register_guest")
        def register_user(user: Guest) -> User:
            registerd_user = self.user_service.register_user(user)
            return registerd_user

        return router

    def _handle_token_from_credential(self, credential: CredentialType) -> str:
        if credential is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credential provided, getting None for credential validation",
            )

        if isinstance(credential, EmailCredential):
            token = self.auth_service.user_login_by_email(
                credential.email, credential.password
            )
        elif isinstance(credential, UserNameCredential):
            token = self.auth_service.user_login_by_user_name(
                credential.user_name, credential.password
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credential type",
            )

        return token

    def __validate_jwt_for_existing_users(self, request: Request) -> bool:
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        if optional_jwt is None:
            return False
        optional_user = self.auth_service.get_user_from_jwt(optional_jwt)
        logger.info(f"[JWT USER FOUND] User: {optional_user}")
        return optional_user is not None
