import logging
import sys
import src.bot as bot

from inspect import getmembers, isfunction
from telebot.types import Message as TgMessage
from telebot.types import CallbackQuery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.ner.models.date_extractor_input import DateExtractorInput
from src.ner.models.message import Message as NerMessage
from src.storage import UserRepository
from src.tg_menu import EventMenuFactory


def configure_handlers():
    """
    Configures handlers \n
    handler is a function which ends with `_handler`, all words before are content types
    """
    handlers = [
        (obj, name.split("_")[:-1])
        for name, obj in getmembers(sys.modules[__name__])
        if (isfunction(obj) and name.endswith("handler"))
    ]
    for handler in handlers:
        bot.settings.bot.message_handler(content_types=handler[1])(handler[0])


def configure_callback_handlers():
    """
    Configures callback handlers \n
    callback handlers is a function which ends with `_callback`, the word before is callback_data prefix
    """
    callbacks = [
        (obj, name.split("_")[:-1])
        for name, obj in getmembers(sys.modules[__name__])
        if (isfunction(obj) and name.endswith("callback"))
    ]
    for callback in callbacks:
        bot.settings.bot.callback_query_handler(func=lambda call: call.data.startswith("_".join(callback[1])))(
            callback[0]
        )


def cancel_callback(call: CallbackQuery):
    """
    Cancel button callback \n
    Deletes specified event
    """
    event_id = call.data.split("_")[1]
    user_repository = UserRepository()
    user = user_repository.get(call.from_user.id)
    if user:
        calendar_service = build("calendar", "v3", credentials=user.google_credentials)
        try:
            calendar_service.events().delete(calendarId="primary", eventId=event_id).execute()
        except HttpError:
            pass
        # XXX: parse_mode="Markdown" doesn't work for some reason
        bot.settings.bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=f"<s>{call.message.text}</s>",
            message_id=call.message.message_id,
            reply_markup=None,
            parse_mode="HTML",
        )


def text_handler(message: TgMessage):
    """
    Message "proccessor" \n
    Extracts datetime from user message and creates google calendar event
    """
    print(bot.settings.bot.get_me().id)
    user_repository = UserRepository()
    user = user_repository.get(message.from_user.id)
    if user and user.is_finished:
        input_data = DateExtractorInput([NerMessage(message_text=message.text, sent_timestamp=message.date)])
        r = bot.settings.ner.extract_date(input_data)
        if not r.is_success:
            bot.settings.bot.send_message(
                message.chat.id, "К сожалению, нам не удалось извлечь дату из этого сообщения."
            )
        else:
            calendar_service = build("calendar", "v3", credentials=user.google_credentials)
            event = {
                "summary": "Personal Secretary Bot event",
                "description": message.text,
                "start": {"dateTime": r._datetime_value.isoformat() + "+03:00", "timeZone": "Europe/Moscow"},
                "end": {"dateTime": r._datetime_value.isoformat() + "+03:00", "timeZone": "Europe/Moscow"},
                "reminders": {
                    "useDefault": True,
                },
            }
            event = calendar_service.events().insert(calendarId="primary", body=event).execute()
            bot.settings.bot.send_message(
                message.chat.id,
                "Событие успешно создано.",
                reply_markup=EventMenuFactory.generate(event.get("id"), event.get("htmlLink")),
            )
    else:
        bot.settings.bot.send_message(message.chat.id, "Вы еще не зарегистрированны. Для регистрации напишите /start.")
