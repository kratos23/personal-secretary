import logging
from typing import Optional
from pydantic import BaseSettings
from telebot import TeleBot
from google_auth_oauthlib.flow import Flow

from src.ner.date_extractor import DateExtractor

google_scopes = ["https://www.googleapis.com/auth/calendar"]


class Settings(BaseSettings):
    log_level: str

    tg_token: str

    google_return_url: str
    google_auth_flow: Optional[Flow]

    db_name: str

    bot: Optional[TeleBot]
    ner: Optional[DateExtractor]

    def __init__(self, init_ner: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = TeleBot(self.tg_token)
        self.google_auth_flow = Flow.from_client_secrets_file(
            "client_secret.json", scopes=google_scopes, redirect_uri=self.google_return_url
        )

        if init_ner:
            self.ner = DateExtractor()

        numeric_level = getattr(logging, self.log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {self.log_level}")
        logging.basicConfig(level=numeric_level)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings(init_ner: bool = False) -> Settings:
    return Settings(init_ner)
