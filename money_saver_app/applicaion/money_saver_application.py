
from typing import Optional
from application.application_config import BaseApplicationConifig
from money_saver_app.applicaion.money_saver_application_config import ApplicationMode, MoneySaverApplicationConfig
from money_saver_app.repository.recorder_repository import TransactionRepository, UserRepository, UserTokenRepository
from money_saver_app.repository.sql_crud_repository import SQLCrudRepository
from money_saver_app.service.money_saver.money_saver_service import MoneySaverService
from money_saver_app.service.pipeline_service.pipeline_impls.pipeline_factory import VoiceDevelopmentPipelineFactory, VoiceProductionPipelineFactory
from money_saver_app.service.voice_recognizer.voice_recognizer_impl.openai_whisper_voice_recognizer import OpenAIWhiswerVoiceRecognizer
from smart_base_model.llm.large_language_model_base import LargeLanguageModelBase
from smart_base_model.llm.llm_impls.ollama_large_language_model import OllamaModel
from smart_base_model.llm.llm_impls.openai_large_language_model import OpenAIModel


class MoneySaverApplication:
    """
    The `MoneySaverApplication` class is the main entry point for the Money Saver application. 
    It is responsible for setting up the necessary dependencies, including the database repositories, the money saver service, the voice recognizer, and the language model.
    The class takes a `MoneySaverApplicationConfig` object as input, which contains the configuration settings for the application, such as the SQL URL, the application mode (development or production), and the language model configuration.
    The class initializes the database repositories, the money saver service, the voice recognizer, and the language model. 
    It then creates the appropriate pipeline factory based on the application mode, which is used to handle the voice recognition and processing workflows.
    The `_get_language_model` method is a helper method that is used to create the appropriate language model based on the configuration settings in the `BaseApplicationConfig` object.
    """
    def __init__(self,app_config: MoneySaverApplicationConfig) -> None:
        self.base_config = app_config.base_config
        self.app_config = app_config


        engine = SQLCrudRepository.create_all_tables(app_config.sql_url)
        self.user_repo = UserRepository(engine)
        self.transaction_repo = TransactionRepository(engine)
        self.user_token_repo = UserTokenRepository()

        self.money_saver_service = MoneySaverService(engine, self.user_repo, self.transaction_repo, self.user_token_repo)
        self.voice_recognizer = OpenAIWhiswerVoiceRecognizer()

        optional_llm = self._get_language_model(app_config.base_config)
        if optional_llm is None:
            raise Exception("[NO MODEL CONFIG PROVIDED] Failed to create language model")
        
        self.llm = optional_llm
        
        match self.app_config.mode:
            case ApplicationMode.PRODUCTION:
                self.pipeline_factory = VoiceProductionPipelineFactory(self.money_saver_service, self.llm, self.voice_recognizer)
            case ApplicationMode.DEVELOPMENT:
                self.pipeline_factory = VoiceDevelopmentPipelineFactory()


    def _get_language_model(self, base_config: BaseApplicationConifig) -> Optional[LargeLanguageModelBase]:

        if "ollama_config" not in base_config and "openai_config" not in base_config:
            raise ValueError("No language model config provided")
        
        ollma_config = base_config.get("ollama_config")
        if ollma_config is not None:
            return OllamaModel(ollma_config)
        
        openai_config = base_config.get("openai_config")
        if openai_config is not None:
            return OpenAIModel(openai_config)
