from typing import Callable, Generic
from linebot.models.send_messages import (
    SendMessage,
    TextSendMessage,
    VideoSendMessage,
    ImageSendMessage,
    StickerSendMessage,
)
from linebot.models.template import TemplateSendMessage, ConfirmTemplate

from pydantic import BaseModel, Field


from typing import Generic, TypeVar

T = TypeVar("T")


class LineSendMessage(SendMessage): ...


class LineTextSendMessage(TextSendMessage): ...


class LineVideoSendMessage(VideoSendMessage): ...


class LineImageSendMessage(ImageSendMessage): ...


class LineStickerSendMessage(StickerSendMessage): ...


class LineTemplateSendMessage(TemplateSendMessage): ...


class LineConfirmTemplate(ConfirmTemplate): ...


class UserProfile(BaseModel):
    display_name: str = Field(alias="displayName")
    language: str = Field(alias="language")
    picture_url: str = Field(alias="pictureUrl")
    user_id: str = Field(alias="userId")


class MessageContext(BaseModel, Generic[T]):
    user_profile: UserProfile
    message_content: T
    reply_message: Callable[[LineSendMessage], None]
