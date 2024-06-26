# please login first

import datetime
from typing import Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from money_saver_app.service.money_saver.auth_service import AuthService


class AuthMiddleware:
    COOKIE_NAME = "jwt"

    def __init__(self, auth_service: AuthService, exclude_routes: list[str]) -> None:
        logger.info(f"[EXCLUDE ROUTE REGISTRATION] Routes: {exclude_routes}")
        self.exclude_routes = exclude_routes
        self.auth_service = auth_service

    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        optional_jwt = request.cookies.get(self.COOKIE_NAME)
        for url in self.exclude_routes:
            if url in str(request.url):
                logger.info(f"[AUTH MIDDLEWARE ROUTE EXCLUDED] Bypass URL: {url}")
                return await call_next(request)

        if optional_jwt is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        jwt_user = self.auth_service.get_jwt_user_from_jwt(optional_jwt)
        if jwt_user is None:
            return JSONResponse(
                content={"detail": "Please login first", "timestamp": utc_time},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        request.state.user = jwt_user
        return await call_next(request)
