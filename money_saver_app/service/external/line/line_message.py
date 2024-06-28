from typing import Any, Callable, Generic, TypeVar

from linebot.models.actions import MessageAction, PostbackAction
from linebot.models.send_messages import (
    ImageSendMessage,
    SendMessage,
    StickerSendMessage,
    TextSendMessage,
    VideoSendMessage,
)
from linebot.models.template import (
    ButtonsTemplate,
    ConfirmTemplate,
    TemplateSendMessage,
)
from pydantic import BaseModel, Field

T = TypeVar("T")


class LineSendMessage(SendMessage): ...


class LineTextSendMessage(TextSendMessage): ...


class LineVideoSendMessage(VideoSendMessage): ...


class LineImageSendMessage(ImageSendMessage): ...


class LineStickerSendMessage(StickerSendMessage): ...


class LineTemplateSendMessage(TemplateSendMessage): ...


class LineButtonTemplate(ButtonsTemplate): ...


class LineConfirmTemplate(ConfirmTemplate): ...


class LineMessageAction(MessageAction): ...


class LinePostBackAction(PostbackAction): ...


class UserProfile(BaseModel):
    display_name: str = Field(alias="displayName")
    language: str = Field(alias="language")
    picture_url: str = Field(alias="pictureUrl")
    user_id: str = Field(alias="userId")


class MessageContext(BaseModel, Generic[T]):
    user_profile: UserProfile
    message_content: T
    reply_message: Callable[[LineSendMessage], Any]
