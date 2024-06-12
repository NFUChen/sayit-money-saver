from enum import Enum
from application.application_config import BaseApplicationConifig


class ApplicationMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class MoneySaverApplicationConfig:
    base_config: BaseApplicationConifig
    sql_url: str
    mode: ApplicationMode
