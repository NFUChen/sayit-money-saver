import datetime
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from money_saver_app.service.money_saver.error_code import ErrorCodeWithError


class ExceptionMiddleware:
    async def __call__(self, request: Request, call_next: Callable):
        utc_time = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            return await call_next(request)
        except ErrorCodeWithError as error_with_code:
            logger.exception(error_with_code)
            return JSONResponse(
                content={"detail": str(error_with_code), "timestamp": utc_time},
                status_code=error_with_code.ERROR_CODE,
            )
        except Exception as base_exception:
            error_message = f"Unhandled internal server error: {str(base_exception)}"
            return JSONResponse(
                content={"detail": error_message, "timestamp": utc_time},
                status_code=500,
            )
