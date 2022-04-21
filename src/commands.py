import sys
import src.bot as bot

from inspect import getmembers, isfunction
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from telebot.types import Message
from src.google import generate_auth_url

from src.storage import UserRepository


def configure_commands():
    """
    Configures commands \n
    command is a function which ends with `_command`, all words before are command aliases
    """
    commands_handlers = [
        (obj, name.split("_")[:-1])
        for name, obj in getmembers(sys.modules[__name__])
        if (isfunction(obj) and name.endswith("command"))
    ]

    for handler in commands_handlers:
        bot.settings.bot.message_handler(commands=handler[1])(handler[0])


def start_command(message: Message):
    """
    /start command \n
    Checks if user is registrated then sends google auth url if not
    """
    user_repository = UserRepository()
    user = user_repository.get_or_create(message.from_user.id)
    if not user.is_finished:
        auth_url = generate_auth_url(message.from_user.id)
        bot.settings.bot.send_message(
            message.chat.id,
            f"Ваша [ссылка для регистрации]({auth_url})",
            parse_mode="Markdown",
        )
    else:
        bot.settings.bot.send_message(message.chat.id, "Вы уже зарегистрированы.", parse_mode="Markdown")
