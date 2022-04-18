from typing import List
from src.ner.models import Message


class DateExtractorInput:
    def __init__(self, messages: List[Message]):
        self.messages = messages
