import os

from dotenv import load_dotenv
from application.application_config import BaseApplicationConfig
from money_saver_app.application.money_saver_application import MoneySaverApplication
from money_saver_app.application.money_saver_application_config import (
    LineServiceConfig,
    MoneySaverApplicationConfig,
)
from money_saver_app.controller.core.voice_money_saver_web_controller import (
    VoiceMoneySaverWebController,
)

def main():
    load_dotenv()
    base_config = BaseApplicationConfig(
        openai_config={
            "api_key": os.environ["OPENAI_API_KEY"],
            "model_name": os.environ["OPENAI_MODEL_NAME"],
            "mode": "json",
        },
        ollama_config={
            "host": os.environ["OLLAMA_HOST"],
            "port": int(os.environ["OLLAMA_PORT"]),
            "model_name": "phi3:medium",
            "mode": "json",
        },
    )
    
    line_service_config = LineServiceConfig(
        channel_secret=os.environ["LINE_CHANNEL_SECRET"],
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"],
    )
    app_config = MoneySaverApplicationConfig(
        base_config,
        os.environ["SQL_URL"],
        {"model_name": "base"},
        {
            "access_token_expire_minutes": 300,
            "secret_key": os.environ["SECRET_KEY"],
        },
        line_service_config,
    )
    app = MoneySaverApplication(app_config)

    app.run_controller(VoiceMoneySaverWebController)

if __name__ == "__main__":
    main()