from date_extractor_package.models import Message


class DateExtractorInput:

    def __init__(self, messages: [Message]):
        self.messages = messages
