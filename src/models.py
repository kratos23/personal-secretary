import json
from typing import Optional
from pydantic import BaseModel
from google.oauth2.credentials import Credentials


class User(BaseModel):
    telegram_id: int
    credentials: Optional[str]
    is_finished: bool

    @property
    def google_credentials(self) -> Credentials:
        creds_dict = json.loads(self.credentials)
        return Credentials.from_authorized_user_info(creds_dict)
