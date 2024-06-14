from typing import Literal, Optional, TypedDict

from fastapi import status

from money_saver_app.repository.models import Role


class LanguageDict(TypedDict):
    """
    A TypedDict representing a language-specific error message.
    The keys in this TypedDict are the language codes, and the values are the corresponding error message strings.
    """

    en: str
    chi: str


class LanguageResource:
    """
    Represents an enumeration of error codes and their corresponding language-specific error messages.

    The `LanguageResource` enum defines a set of error codes, each with a dictionary of language-specific error messages. The keys in the dictionary are the language codes, and the values are the corresponding error message strings.

    This enum is used to provide localized error messages for different languages when an error occurs in the application.
    """

    USER_NOT_FOUND: LanguageDict = {
        "en": "User not found - ID: {user_id}, EMAIL: {user_email}",
        "chi": "使用者不存在- ID: {user_id}, EMAIL: {user_email}",
    }

    TOKEN_NOT_FOUND: LanguageDict = {
        "en": "Token not found: {token}",
        "chi": "Token不存在: {token}",
    }
    OPTIONAL_TEXT_MISSING: LanguageDict = {
        "en": "Transcribed text is missing, transcription failed.",
        "chi": "字體未翻譯成功",
    }
    OPTIONAL_TRANSCRIPTION_VIEW_NOT_FOUND: LanguageDict = {
        "en": "交易紀錄未成功紀錄 原始記錄: {source}",
        "chi": "Transaction view not found for the given optional text and model. Source: {source}",
    }

    PASSWORD_NOT_MATCH: LanguageDict = {
        "en": "The password does not match",
        "chi": "使用者密碼錯誤",
    }

    ROLE_PERMISSION_DENIED: LanguageDict = {
        "en": "Role permission denied: {required_role}, actual roles: {actual_role}",
        "chi": "使用者權限不足: {required_role}, 實際權限: {actual_role}",
    }
    EMAIL_DUPLICATE: LanguageDict = {
        "en": "The email has been registered.",
        "chi": "該電子郵件已經被註冊",
    }
    TRASACTION_PARSER_ERROR: LanguageDict = {
        "en": "Unable to parse transaction, please try it again...",
        "chi": "未能成功解析交易紀錄, 請重新嘗試...",
    }


class ErrorCodeWithError(Exception):
    """
    Represents a base exception class for error codes with associated error messages.

    The `ErrorCodeWithError` class is a base exception class that provides a standard way to represent errors with associated error codes and localized error messages.
    It is intended to be subclassed by more specific error classes.

    The class has the following attributes:

    - `LANGUAGE`: A literal type representing the language of the error message. The default value is `"chi"`.
    - `ERROR_CODE`: An integer representing the error code. The default value is `500`.

    When an instance of `ErrorCodeWithError` or a subclass is created, the following arguments are passed to the constructor:

    - `error_code`: An integer representing the error code.
    - `message_template`: A string representing the error message template, which can contain placeholders for additional information.
    - `**kwargs`: Additional keyword arguments that will be used to format the error message template.

    The `__str__` method returns a formatted error message string that includes the error code and the formatted error message.
    """

    LANGUAGE: Literal["chi", "en"] = "chi"
    ERROR_CODE: int = 500

    def __init__(self, error_code: int, message_template: str, **kwargs) -> None:
        self.code = error_code
        self.message_template = message_template

        self.error_kwargs = kwargs

    def __str__(self) -> str:
        return self.message_template.format(**self.error_kwargs)


class OptionalTextMissingError(ErrorCodeWithError):
    ERROR_CODE: int = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self) -> None:
        super().__init__(
            self.ERROR_CODE, LanguageResource.OPTIONAL_TEXT_MISSING[self.LANGUAGE]
        )


class TransactionViewNotFoundError(ErrorCodeWithError):
    ERROR_CODE: int = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, text: str = "") -> None:
        super().__init__(
            self.ERROR_CODE,
            "Transaction view not found for the given text.",
            source=text,
        )


class UnableToParseViewRequestError(ErrorCodeWithError):
    ERROR_CODE: int = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, text: str = "") -> None:
        super().__init__(
            self.ERROR_CODE,
            LanguageResource.TRASACTION_PARSER_ERROR[self.LANGUAGE],
            source=text,
        )


class RolePermissionDenied(ErrorCodeWithError):
    ERROR_CODE = status.HTTP_401_UNAUTHORIZED

    def __init__(self, required_role: Role, actual_role: Role) -> None:
        super().__init__(
            self.ERROR_CODE,
            LanguageResource.ROLE_PERMISSION_DENIED[self.LANGUAGE].format(
                required_role=required_role, actual_role=actual_role
            ),
        )


class PasswordNotMatchError(ErrorCodeWithError):
    ERROR_CODE = status.HTTP_401_UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__(
            self.ERROR_CODE, LanguageResource.PASSWORD_NOT_MATCH[self.LANGUAGE]
        )


class UserNotFoundError(ErrorCodeWithError):
    ERROR_CODE = status.HTTP_404_NOT_FOUND

    def __init__(
        self, user_id: Optional[int] = None, user_email: Optional[str] = None
    ) -> None:
        super().__init__(
            self.ERROR_CODE,
            LanguageResource.USER_NOT_FOUND[self.LANGUAGE],
            user_id=user_id,
            user_email=user_email,
        )


class EmailDuplicationError(ErrorCodeWithError):
    ERROR_CODE = status.HTTP_409_CONFLICT

    def __init__(self) -> None:
        super().__init__(
            self.ERROR_CODE, LanguageResource.EMAIL_DUPLICATE[self.LANGUAGE]
        )
