import unittest

import src.ner
from src.ner import Message


class DateExtractorTestCase(unittest.TestCase):
    _date_extractor = src.ner.DateExtractor()

    def test_date_interval(self):
        self._preform_test_expect_time([
            Message("я думаю имеет смысл сразу после встретиться (я думаю это 16:30-17:00)",
                    1648195080),
            Message("Согласен", 1648197960),
            Message(""""Посадка" на ленинградском вокзале""", 1648197965),
            Message("""Щас это конечно звучит""", 1648197970),
            Message(""")))))""", 1648198860)
        ], 1648215000)  # пятница, 25 марта 2022 г., 16:30:00 GMT+03:00

    def test_hour_only(self):
        self._preform_test_expect_time(
            [
                Message("Че тогда", 1648294861),
                Message("В 17 часов", 1648294862),
                Message("Земляной вал 8", 1648294863),
                Message("(?)", 1648294864),
            ], 1648303200)  # суббота, 26 марта 2022 г., 17:00:00 GMT+03:00

    def test_weekday_and_time(self):
        self._preform_test_expect_time(
            [
                Message(
                    "Получается можно распределять задачи."
                    " @demist когда можно с вами созвониться, для распределения задач?",
                    1642260600
                ),
                Message(
                    "Добрый день!",
                    1642260601
                ),
                Message(
                    "Давайте во вторник во второй половине дня."
                    "Например, в 17:00",
                    1642260602
                ),
                Message(
                    "ок?",
                    1642260603
                ),
                Message(
                    "мне ок",
                    1642260604
                ),

            ],
            1642514400)  # вторник, 18 января 2022 г., 17:00:00 GMT+03:00

    def test_work_meeting(self):
        self._preform_test_expect_time(
            [
                Message(
                    "Привет, нужно синкануться по блендеру, когда сегодня будет время?",
                    1643878740
                ),
                Message(
                    "Привет, давай между 12:30 и 16:00",
                    1643878741
                ),
                Message(
                    "поставлю на 12:30 тогда",
                    1643878742
                ),
                Message(
                    "Тебе нужна переговорка?",
                    1643878743
                ),
                Message(
                    "Нет,я пока дома",
                    1643878744
                )
            ],
            1643880600
        )

    def test_day_relative_and_time(self):
        self._preform_test_expect_time(
            [
                Message(
                    """@yyr_7 @iamhappyasfuck Предлагаю собраться завтра (12.02), для написания общего тз""",
                    1644583680
                ),
                Message(
                    """свое скину сегодня вечером. вам будет удобно собраться завтра после 22:00, или слишком поздно?""",
                    1644583681
                ),
                Message(
                    """просто завтра я только в это время смогу""",
                    1644583682
                ),
                Message(
                    """Мне норм""",
                    1644583683
                ),
                Message(
                    """Норм""",
                    1644583684
                ),
            ],
            1644692400)  # суббота, 12 февраля 2022 г., 22:00:00 GMT+03:00

    def test_today_and_time_only_one_message(self):
        self._preform_test_expect_time(
            [
                Message(
                    "напоминаю, что сегодня в 19:00 состоится чемпионат мира по покеру в черной пятнице",
                    1647606900
                )
            ],
            1647619200
        )  # пятница, 18 марта 2022 г., 19:00:00 GMT+03:00

    def test_no_date_time_in_messages(self):
        self._preform_test_expect_failure(
            [
                Message(
                    "так",
                    1649594016
                ),
                Message(
                    "у меня вопрос к тебе",
                    1649594017
                ),
                Message(
                    "как к эксперту разработки",
                    1649594018
                ),
                Message(
                    "смотри",
                    1649594019
                ),
                Message(
                    "у меня условно есть ветка main, а есть data_loader (которую я периодически мерджу в main)",
                    1649594020
                ),
                Message(
                    "потом я ответвился от data_loader на ветку batching",
                    1649594021
                ),
                Message(
                    "все там реализовал",
                    1649594022
                ),
                Message(
                    "насколько норм тема их локально померджить, чтобы продолжить в data_loader работать ?...",
                    1649594023
                ),
                Message(
                    "кого с кем?",
                    1649594024
                ),
                Message(
                    "batching и data_loader",
                    16495940125
                ),
            ]
        )

    def test_sorting_checked(self):
        self.assertRaises(ValueError, self._extract_date, [
            Message("some text", 2),
            Message("some text", 1)
        ])

    def test_today_and_time_only_one_message_eng(self):
        self._preform_test_expect_time(
            [
                Message(
                    "I remind you that today at 19:00 the Black Friday Poker World Championship will take place",
                    1647606900
                )
            ],
            1647619200
        )  # пятница, 18 марта 2022 г., 19:00:00 GMT+03:00


    def _preform_test_expect_time(self, messages: [Message], expected_time_stamp):
        result = self._extract_date(messages)
        self.assertEqual(expected_time_stamp, result.get_date_time().timestamp())

    def _preform_test_expect_failure(self, messages: [Message]):
        result = self._extract_date(messages)
        self.assertFalse(result.is_success())
        self.assertIsNone(result.get_date_time())

    def _extract_date(self, messages: [Message]):
        return self._date_extractor.extract_date(src.ner.DateExtractorInput(messages))


if __name__ == '__main__':
    unittest.main()
