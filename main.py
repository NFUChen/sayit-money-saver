from application.application_config import BaseApplicationConifig
from money_saver_app.applicaion.money_saver_application import MoneySaverApplication
from money_saver_app.applicaion.money_saver_application_config import (
    ApplicationMode,
    MoneySaverApplicationConfig,
)
from money_saver_app.controller.fastapi.voice_money_saver_web_controller import (
    VoiceMoneySaverWebController,
)


def main():
    base_config = BaseApplicationConifig(
        openai_config={"api_key": "", "mode": "json", "model_name": ""},
        ollama_config={
            "host": "10.3.139.93",  # 10.3.139.93
            "port": 11434,
            "model_name": "phi3:medium",
            "mode": "json",
        },
    )
    app_config = MoneySaverApplicationConfig(
        base_config,
        "sqlite:///test.db",
        ApplicationMode.PRODUCTION,
        {"model_name": "base"},
    )
    app = MoneySaverApplication(app_config)

    app.run_controller(VoiceMoneySaverWebController)


if __name__ == "__main__":
    main()
