from datetime import datetime
from typing import Union


class DateExtractorResult:
    def __init__(self, datetime_value: Union[datetime, None]):
        self._datetime_value = datetime_value

    @classmethod
    def success(cls, datetime):
        return cls(datetime)

    @classmethod
    def failure(cls):
        return cls(None)

    def get_date_time(self):
        return self._datetime_value

    @property
    def is_success(self):
        return self._datetime_value is not None

    def __str__(self) -> str:
        return self._datetime_value.__str__()
