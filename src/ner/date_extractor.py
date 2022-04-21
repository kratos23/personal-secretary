from datetime import datetime
import logging
from typing import List

import dateparser
from dateparser.search import search_dates
from deeppavlov import configs, build_model

from src.ner.models import *
from src.ner.models import Message
from src.ner.models.date_extractor_input import DateExtractorInput

from src.ner.models.date_extractor_result import DateExtractorResult


class DateExtractor:
    _NER_B_TIME = "B-TIME"
    _NER_I_TIME = "I-TIME"
    _NER_B_DATE = "B-DATE"
    _NER_I_DATE = "I-DATE"

    def __init__(self):
        self._ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)

    _date_parser_settings = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PARSERS": ["custom-formats", "absolute-time", "timestamp"],
        "SKIP_TOKENS": ["-", "T"],
    }
    _date_parser_languages = ["ru", "en"]
    _date_parser_formats = ["%d.%m", "%d.%m.%Y"]

    def extract_date(self, extractor_input: DateExtractorInput) -> DateExtractorResult:
        messages_text = self._get_messages_as_text_list(extractor_input.messages)
        (result_text, result_entities) = self._ner_model(messages_text)
        parsed_dates = []
        relative_base = extractor_input.messages[0].sent_timestamp
        for i in range(len(result_text)):
            cur_text = result_text[i]
            cur_entities = result_entities[i]
            source_text = messages_text[i]
            time_strs = self._extract_time_string(cur_text, cur_entities, source_text, self._is_time_entity)
            time_strs += self._extract_time_string(cur_text, cur_entities, source_text, self._is_date_entity)
            if time_strs is not None:
                for time_str in time_strs:
                    if time_str is not None:
                        parsed_data = self._parse_time_string(time_str, relative_base)
                        if parsed_data is not None:
                            parsed_dates.append(parsed_data)

        if len(parsed_dates) > 0:
            return DateExtractorResult.success(self._merge_dates(parsed_dates, relative_base))
        else:
            return DateExtractorResult.failure()

    def _merge_dates(self, dates: List[datetime], relative_base_timestamp: int) -> datetime:
        day_begin_moments = []
        for cur_date in dates:
            day_begin_moments.append(datetime(cur_date.year, cur_date.month, cur_date.day))

        result_date = day_begin_moments[0]
        for possible_date in day_begin_moments:
            if result_date.timestamp() - relative_base_timestamp < possible_date.timestamp() - relative_base_timestamp:
                result_date = possible_date

        time = dates[0]
        for cur_date in dates:
            if cur_date.hour != 0 or cur_date.minute != 0 or cur_date.second != 0:
                time = cur_date
                break
        result_date = result_date.replace(
            hour=time.hour, minute=time.minute, second=time.second, microsecond=time.microsecond
        )

        return result_date

    def _get_messages_as_text_list(self, messages_list: List[Message]) -> List[str]:
        result = []
        for message in messages_list:
            result.append(message.message_text)
        for i in range(1, len(messages_list)):
            prev_message = messages_list[i - 1]
            cur_message = messages_list[i]
            if cur_message.sent_timestamp < prev_message.sent_timestamp:
                raise ValueError("Messages must be sorted via sent_timestamp")
        return result

    def _extract_time_string(
        self, text: List[str], entities: List[str], source_text: str, is_valid_entity
    ) -> List[str]:
        assert len(text) == len(entities)

        _STATE_IDLE = 0
        _STATE_ACTIVE = 1
        _STATE_ENDED = 2
        state = _STATE_IDLE

        word_groups = []
        time_words = []
        text_pos = 0
        if len(text) == 0:
            state = _STATE_ENDED
        while state != _STATE_ENDED:
            cur_entity = entities[text_pos]
            cur_text = text[text_pos]

            if state == _STATE_IDLE:
                if is_valid_entity(cur_entity):
                    time_words.append(cur_text)
                    state = _STATE_ACTIVE
            elif state == _STATE_ACTIVE:
                if not is_valid_entity(cur_entity):
                    word_groups.append(time_words.copy())
                    time_words.clear()
                    state = _STATE_IDLE
                else:
                    time_words.append(cur_text)

            text_pos += 1
            if text_pos >= len(text):
                word_groups.append(time_words.copy())
                state = _STATE_ENDED

        result = []
        for word_group in word_groups:
            result.append(self._extract_words_from_source(source_text, word_group))

        return result

    def _extract_words_from_source(self, source_text: str, words: List[str]):
        expected_str = "".join(words)
        for left in range(0, len(source_text)):
            for right in range(left + 1, len(source_text) + 1):
                cur_str = source_text[left:right]
                if cur_str.replace(" ", "") == expected_str:
                    return cur_str.strip()
        return None

    def _parse_time_string(self, time_str: str, relative_base_timestamp: int):
        time_str = time_str.replace("-", " ")
        time_str = self._replace_plain_hours(time_str)

        cur_settings = self._date_parser_settings.copy()
        cur_settings["RELATIVE_BASE"] = datetime.fromtimestamp(relative_base_timestamp)
        time_result = dateparser.parse(
            date_string=time_str,
            settings=cur_settings,
            date_formats=self._date_parser_formats,
            languages=self._date_parser_languages,
        )
        if time_result is not None:
            return time_result
        else:
            found_dates = search_dates(text=time_str, settings=cur_settings, languages=self._date_parser_languages)
            if found_dates is not None:
                return found_dates[0][1]
            else:
                return None

    _plain_hours_replacement = {
        "1 час": "13:00",
        "2 часа": "14:00",
        "3 часа": "15:00",
        "4 часа": "16:00",
        "5 часов": "17:00",
        "6 часов": "18:00",
        "7 часов": "19:00",
        "8 часов": "20:00",
        "9 часов": "21:00",
        "10 часов": "22:00",
        "11 часов": "23:00",
        "12 часов": "12:00",
        "13 часов": "13:00",
        "14 часов": "14:00",
        "15 часов": "15:00",
        "16 часов": "16:00",
        "17 часов": "17:00",
        "18 часов": "18:00",
        "19 часов": "19:00",
        "20 часов": "20:00",
        "21 час": "21:00",
        "22 часа": "22:00",
        "23 часа": "23:00",
    }

    def _replace_plain_hours(self, time_str):
        if time_str in self._plain_hours_replacement:
            return self._plain_hours_replacement[time_str]
        else:
            return time_str

    def _is_time_entity(self, entity_name):
        return entity_name == self._NER_B_TIME or entity_name == self._NER_I_TIME

    def _is_date_entity(self, entity_name):
        return entity_name == self._NER_B_DATE or entity_name == self._NER_I_DATE
