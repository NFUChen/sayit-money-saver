from fastapi import Request

from money_saver_app.service.money_saver.auth_service import JWTUser


def get_current_user_id(request: Request) -> int:
    user: JWTUser = request.state.user
    return user["id"]
