from abc import ABC
from dataclasses import dataclass
from typing import Type, Union

from linebot import LineBotApi, WebhookHandler
from loguru import logger
from passlib.context import CryptContext

from application.application_config import BaseApplicationConfig
from money_saver_app.application.money_saver_application_config import (
    ApplicationMode,
    MoneySaverApplicationConfig,
)
from money_saver_app.controller.core.router_controller import RouterController
from money_saver_app.controller.external.line.line_controller import (
    LineServiceRouteController,
    MessageContext,
)
from money_saver_app.repository.recorder_repository import (
    ExternalUserRepository,
    TransactionRepository,
    UserRepository,
)
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository
from money_saver_app.service.external.line.line_notification_service import (
    LineNotificationService,
)
from money_saver_app.service.money_saver.auth_service import AuthService
from money_saver_app.service.money_saver.money_saver_service import MoneySaverService
from money_saver_app.service.money_saver.transaction_service import TransactionService
from money_saver_app.service.money_saver.user_service import UserService
from money_saver_app.service.pipeline_service.pipeline_impls.pipeline_factory import (
    TextPipelineFactory,
    VoiceDevelopmentPipelineFactory,
    VoicePipelineFactory,
)
from money_saver_app.service.voice_recognizer.voice_recognizer_impl.openai_whisper_voice_recognizer import (
    OpenAIWhisperVoiceRecognizer,
)
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase
from smart_base_model.llm.llm_impls.openai_large_language_model import OpenAIModel
from smart_base_model.messaging.behavior_subject import BehaviorSubject


@dataclass
class MoneySaverController(ABC):
    app_config: MoneySaverApplicationConfig
    user_service: UserService
    auth_service: AuthService
    money_saver_service: MoneySaverService
    transaction_service: TransactionService
    external_controllers: list[RouterController]

    def run(self) -> None: ...


class MoneySaverApplication:
    """
    The `MoneySaverApplication` class is the main entry point for the Money Saver application. It is responsible for setting up and managing the various components of the application, including the language model, voice recognizer, user and transaction services, and external service controllers.
    The `__init__` method initializes the application configuration, language model, password context, voice recognizer, user and transaction repositories, and various service components. It also sets up the LINE bot API and webhook handler, and creates the external service controllers.
    The `_get_language_model` method is a helper function that selects the appropriate language model based on the application configuration.
    The `run_controller` method is used to run a specific `MoneySaverController` instance, which is responsible for handling the application's core functionality.
    """

    def __init__(self, app_config: MoneySaverApplicationConfig) -> None:
        self.base_config = app_config.base_config
        self.app_config = app_config

        self.llm = self._get_language_model(app_config.base_config)
        logger.info(f"[MODEL SELECTION] Select LLM: {self.llm.get_model_name()}")

        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.voice_recognizer = OpenAIWhisperVoiceRecognizer(
            app_config.openai_whisper_config
        )

        engine = SQLCrudRepository.create_all_tables(app_config.sql_url)
        self.user_repo = UserRepository(engine)
        self.external_user_repo = ExternalUserRepository(engine)

        self.user_service = UserService(
            engine, self.user_repo, self.external_user_repo, self.password_context
        )
        self.auth_service = AuthService(
            self.user_service, self.password_context, app_config.jwt_config
        )
        self.transaction_repo = TransactionRepository(engine)

        self.transaction_service = TransactionService(
            engine, self.user_repo, self.transaction_repo
        )

        match self.app_config.mode:
            case ApplicationMode.PRODUCTION:
                self.voice_pipeline_factory = VoicePipelineFactory()
                self.text_pipeline_factory = TextPipelineFactory()
            case ApplicationMode.DEVELOPMENT:
                self.pipeline_factory = VoiceDevelopmentPipelineFactory()

        self.money_saver_service = MoneySaverService(
            engine,
            self.voice_pipeline_factory,
            self.text_pipeline_factory,
            self.user_service,
            self.transaction_service,
            self.llm,
            self.voice_recognizer,
        )

        self.webhook_handler = WebhookHandler(
            self.app_config.line_service_config.channel_secret
        )
        self.line_bot_api = LineBotApi(
            self.app_config.line_service_config.channel_access_token
        )
        self.line_message_context = BehaviorSubject[MessageContext[Union[str, bytes]]]()

        self.external_service_controllers: list[RouterController] = [
            LineServiceRouteController(
                self.voice_recognizer,
                self.llm,
                "/api/public/line",
                self.transaction_service,
                self.money_saver_service,
                self.user_service,
                self.line_bot_api,
                self.webhook_handler,
                self.line_message_context,
            )
        ]

        self.line_notification_service = LineNotificationService(
            self.line_bot_api, self.user_service, self.transaction_service
        )

        self._handle_logger()
        self.line_notification_service.schedule_auto_push_notification()

    def _handle_logger(self) -> None:
        logger.add("./log/server.log", rotation="1 day", retention="1 month")

    def _get_language_model(
        self, base_config: BaseApplicationConfig
    ) -> LargeLanguageModelBase:
        if "ollama_config" not in base_config and "openai_config" not in base_config:
            raise ValueError("No language model config provided")

        # ollma_config = base_config.get("ollama_config")
        # if ollma_config is not None:
        #     return OllamaModel(ollma_config)

        openai_config = base_config.get("openai_config")
        if openai_config is not None:
            return OpenAIModel(openai_config)

        raise Exception("[NO MODEL CONFIG PROVIDED] Failed to create language model")

    def run_controller(self, controller_cls: Type[MoneySaverController]) -> None:
        controller_cls(
            self.app_config,
            self.user_service,
            self.auth_service,
            self.money_saver_service,
            self.transaction_service,
            self.external_service_controllers,
        ).run()
