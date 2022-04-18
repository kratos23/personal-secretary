from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class EventMenuFactory:
    @staticmethod
    def generate(event_id: str, event_url: str) -> InlineKeyboardMarkup:
        menu = InlineKeyboardMarkup()
        cancel_btn = InlineKeyboardButton(text="Отменить", callback_data=f"cancel_{event_id}")
        event_btn = InlineKeyboardButton(text="Открыть", url=event_url)
        menu.add(cancel_btn)
        menu.add(event_btn)

        return menu
