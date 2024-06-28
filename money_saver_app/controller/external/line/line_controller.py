from enum import Enum
from typing import Any, Callable, Optional, Union, cast
from uuid import UUID

from fastapi import APIRouter, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models.events import MessageEvent, PostbackEvent
from linebot.models.messages import AudioMessage, TextMessage
from loguru import logger
from openai import BaseModel

from money_saver_app.controller.core.router_controller import RouterController
from money_saver_app.repository.models import TransactionRead
from money_saver_app.service.external.line.line_message import (
    LineButtonTemplate,
    LinePostBackAction,
    LineSendMessage,
    LineTemplateSendMessage,
    LineTextSendMessage,
    MessageContext,
    UserProfile,
)
from money_saver_app.service.money_saver.money_saver_service import MoneySaverService
from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.user_service import UserService
from money_saver_app.service.money_saver.views import (
    AssistantActionType,
    AssistantActionView,
)
from money_saver_app.service.pipeline_service.pipeline_impls.voice_pipeline_step import (
    MoneySaverPipelineContext,
)
from money_saver_app.service.voice_recognizer.voice_recognizer import VoiceRecognizer
from money_saver_app.utils import threaded
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase
from smart_base_model.messaging.behavior_subject import BehaviorSubject


class TransactionOperationType(Enum):
    AddTransaction = "AddTransaction"
    DeleteTransaction = "DeleteTransaction"


class TransactionActionView(BaseModel):
    operation_type: TransactionOperationType
    transaction_id: Optional[UUID] = None


class LineServiceRouteController(RouterController):
    def __init__(
        self,
        voice_recognizer: VoiceRecognizer,
        model_llm: LargeLanguageModelBase,
        router_prefix: str,
        transaction_service: TransactionService,
        money_saver_service: MoneySaverService,
        user_servcie: UserService,
        line_bot_api: LineBotApi,
        webhook_handler: WebhookHandler,
        message_context_subject: BehaviorSubject[MessageContext[Union[str, bytes]]],
    ) -> None:
        self.voice_recognizer = voice_recognizer
        self.llm = model_llm
        self.transaction_service = transaction_service
        self.money_saver_service = money_saver_service
        self.user_servcie = user_servcie
        self.router_prefix = router_prefix
        self.router = APIRouter(prefix=self.router_prefix)
        # 必須放上自己的Channel Access Token
        self.line_bot_api = line_bot_api
        # 必須放上自己的Channel Secret
        self.handler = webhook_handler
        self.message_context_subject = message_context_subject

        self.message_context_subject.subscribe(self._handle_line_audio_message)
        self.message_context_subject.subscribe(self._handle_line_text_message)

    def register_routes(self) -> APIRouter:
        @self.router.post("/callback")
        async def callback(request: Request):
            # get X-Line-Signature header value
            signature = request.headers["X-Line-Signature"]
            logger.info(signature)

            # get request body as text
            body = await request.body()
            body_text = body.decode("utf-8")
            logger.info(body_text)

            # handle webhook body
            try:
                self.handler.handle(body_text, signature)
            except InvalidSignatureError:
                logger.critical(
                    "Invalid signature. Please check your channel access token/channel secret."
                )

            return "OK"

        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event: MessageEvent):
            user_profile = UserProfile.model_validate(
                self.line_bot_api.get_profile(event.source.user_id).as_json_dict()
            )
            logger.info(
                f"[LINE MESSAGE] User {user_profile} Message: {event.message.text}"
            )

            def reply_message_wrapper(message: LineSendMessage) -> None:
                self.line_bot_api.reply_message(event.reply_token, message)

            self.message_context_subject.next(
                MessageContext(
                    user_profile=user_profile,
                    message_content=event.message.text,
                    reply_message=reply_message_wrapper,
                )
            )

        @self.handler.add(MessageEvent, message=AudioMessage)
        def handle_audio_message(event: MessageEvent):
            user_profile = UserProfile.model_validate(
                self.line_bot_api.get_profile(event.source.user_id).as_json_dict()
            )
            audio_binary = self.line_bot_api.get_message_content(
                event.message.id
            ).content

            logger.info(
                f"[LINE MESSAGE] User: {user_profile} Audio Message: {event.message}"
            )

            def reply_message_wrapper(message: LineSendMessage) -> None:
                self.line_bot_api.reply_message(event.reply_token, message)

            self.message_context_subject.next(
                MessageContext(
                    user_profile=user_profile,
                    message_content=audio_binary,
                    reply_message=reply_message_wrapper,
                )
            )

        @self.handler.add(PostbackEvent)
        def handle_postback_message(event: PostbackEvent):
            transaction_action_view = TransactionActionView.model_validate_json(
                cast(str, event.postback.data)
            )

            def reply_message_wrapper(message: LineSendMessage) -> None:
                self.line_bot_api.reply_message(event.reply_token, message)

            self._handle_action_view(transaction_action_view, reply_message_wrapper)

        return self.router

    def _handle_action_view(
        self,
        transaction_action_view: TransactionActionView,
        reply_message: Callable[[LineSendMessage], Any],
    ) -> None:
        if transaction_action_view.transaction_id is None:
            return

        if (
            transaction_action_view.operation_type
            == TransactionOperationType.DeleteTransaction
        ):
            logger.info(
                f"[TRANSACTION ACTION OPERATION] Delete Transaction: {transaction_action_view.transaction_id}"
            )
            is_deleted = self.transaction_service.delete_transaction_by_id(
                transaction_action_view.transaction_id
            )
            if is_deleted:
                logger.info(
                    f"[TRANSACTION DELETION] Transaction with id {transaction_action_view.transaction_id} deleted."
                )
                reply_message(
                    LineTextSendMessage(
                        text=f"已刪除該交易: {transaction_action_view.transaction_id}"
                    )
                )
            return
        if (
            transaction_action_view.operation_type
            == TransactionOperationType.AddTransaction
        ):
            if not self.transaction_service.is_transaction_exists_by_id(
                transaction_action_view.transaction_id
            ):
                reply_message(
                    LineTextSendMessage(
                        text=f"該交易已不存在: {transaction_action_view.transaction_id}"
                    )
                )
            else:
                reply_message(
                    LineTextSendMessage(
                        text=f"已新增該交易: {transaction_action_view.transaction_id}"
                    )
                )

    def __handle_add_transaction(
        self, source_text: str, user_id: int
    ) -> MoneySaverPipelineContext:
        pipeline_context = self.money_saver_service.execute_text_pipeline(
            source_text, user_id=user_id
        )
        logger.info(f"[PIPELINE FINISHED CONTEXT] {pipeline_context}")
        return pipeline_context

    def __format_transaction_read(self, read: TransactionRead) -> str:
        if read.created_at is not None:
            formatted_datetime = read.created_at.strftime("%m/%d/%Y %H:%M:%S")
        return f"[{formatted_datetime} | {read.transaction_type.name} | {read.item.item_category}] {read.item.name}: {read.amount}"

    def _create_template_message_for_pipeline_context(
        self, context: MoneySaverPipelineContext
    ) -> Optional[LineTemplateSendMessage]:
        if context.transaction_read is None:
            return

        delete_action = TransactionActionView(
            operation_type=TransactionOperationType.DeleteTransaction,
            transaction_id=context.transaction_read.id,
        ).model_dump_json()

        add_action = TransactionActionView(
            operation_type=TransactionOperationType.AddTransaction,
            transaction_id=context.transaction_read.id,
        ).model_dump_json()

        return LineTemplateSendMessage(
            alt_text="Confirm for adding transaction",
            template=LineButtonTemplate(
                title="你確定要新增此筆交易嘛",
                text=self.__format_transaction_read(context.transaction_read),
                actions=[
                    LinePostBackAction(
                        label="新增", display_text="確定新增", data=add_action
                    ),
                    LinePostBackAction(
                        label="取消", display_text="確定取消", data=delete_action
                    ),
                ],
            ),
        )

    def __handle_text_message_with_reply_message(
        self, text_message: str, line_user_id: str
    ) -> Optional[LineSendMessage]:
        logger.info(
            f"[RECEIVING LINE MESSAGE] User ID: {line_user_id}, Message: {text_message}"
        )
        # register user if user not exists, user name = line id
        user = self.user_servcie.register_line_user(line_user_id)
        logger.info(f"[LINE USER] {user}")

        action = AssistantActionView.model_ask(text_message, self.llm)
        if action is None:
            logger.warning(f"[INVALID ACTION] {action}")
            return

        logger.info(f"[LINE MESSAGE ACTION] {action}")
        message: Optional[LineSendMessage] = None
        match action.action_type:
            case AssistantActionType.AddTransaction:
                context = self.__handle_add_transaction(
                    source_text=text_message, user_id=cast(int, user.id)
                )
                message = self._create_template_message_for_pipeline_context(context)
                logger.info(f"[LINE MESSAGE RESPONSE] {message}")
                return message
            case AssistantActionType.Reporting:
                message = LineTextSendMessage(
                    "Sorry, I can't do reporting yet. Please try again later."
                )
                logger.info(f"[LINE MESSAGE RESPONSE] {message}")
                return message

    @threaded
    def _handle_line_text_message(
        self, message_context: MessageContext[Union[str, bytes]]
    ) -> None:
        if not isinstance(message_context.message_content, str):
            return
        user_message = message_context.message_content
        reply_message = self.__handle_text_message_with_reply_message(
            user_message, message_context.user_profile.user_id
        )
        if reply_message is None:
            return

        message_context.reply_message(reply_message)

    @threaded
    def _handle_line_audio_message(
        self, message_context: MessageContext[Union[str, bytes]]
    ) -> None:
        if not isinstance(message_context.message_content, bytes):
            return

        user_message = self.voice_recognizer.recognize(message_context.message_content)
        reply_message = self.__handle_text_message_with_reply_message(
            user_message, message_context.user_profile.user_id
        )
        if reply_message is None:
            return
        message_context.reply_message(reply_message)
