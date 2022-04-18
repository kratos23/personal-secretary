from src.handlers import configure_handlers, configure_callback_handlers
from src.settings import get_settings
from src.commands import configure_commands

settings = get_settings(init_ner=True)


def run() -> None:
    """
    Launch telegram bot
    """
    configure_commands()
    configure_handlers()
    configure_callback_handlers()
    settings.bot.polling(none_stop=True)
