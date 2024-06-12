from typing import Literal, TypedDict


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
        "en": "User not found: {user_id}",
        "chi": "使用者不存在: {user_id}",
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


class ErrorCodeWithError(Exception):
    LANGUAGE: Literal["chi", "en"] = "chi"
    ERROR_CODE: int = 500

    def __init__(self, error_code: int, message_template: str, **kwargs) -> None:
        self.code = error_code
        self.message_template = message_template

        self.error_kwargs = kwargs

    def __str__(self) -> str:
        return (
            f"[{self.ERROR_CODE}] {self.message_template.format(**self.error_kwargs)}"
        )


class UserNotFoundError(ErrorCodeWithError):
    ERROR_CODE = 404

    def __init__(self, user_id: int) -> None:
        super().__init__(
            self.ERROR_CODE,
            LanguageResource.USER_NOT_FOUND[self.LANGUAGE],
            user_id=user_id,
        )


class TokenNotFoundError(ErrorCodeWithError):
    ERROR_CODE = 404

    def __init__(self, token: str) -> None:
        super().__init__(
            self.ERROR_CODE,
            LanguageResource.TOKEN_NOT_FOUND[self.LANGUAGE],
            token=token,
        )


class OptionalTextMissingError(ErrorCodeWithError):
    ERROR_CODE: int = 400

    def __init__(self) -> None:
        super().__init__(
            self.ERROR_CODE, LanguageResource.OPTIONAL_TEXT_MISSING[self.LANGUAGE]
        )


class TransactionViewNotFoundError(ErrorCodeWithError):
    LANGUAGE: Literal["chi", "en"] = "en"
    ERROR_CODE: int = 404

    def __init__(self, text: str = "") -> None:
        super().__init__(
            self.ERROR_CODE,
            "Transaction view not found for the given text.",
            source=text,
        )
