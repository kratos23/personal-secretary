import emoji
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.settings import get_settings
from src.storage import UserRepository

app = FastAPI()
settings = get_settings()


@app.get("/callback")
async def callback(state: int, code: str):
    """
    Google OAuth2 callback
    https://developers.google.com/identity/protocols/oauth2/web-server#sample-oauth-2.0-server-response
    """
    # TODO: handle errros(validate `tokens` dict via pydantic model)
    settings.google_auth_flow.fetch_token(code=code)
    user_repository = UserRepository()
    user = user_repository.get_or_create(state)
    if not user.is_finished:
        user_repository.update(id=state, credentials=settings.google_auth_flow.credentials.to_json(), is_finished=True)
        settings.bot.send_message(state, "Вы успешно зарегистрированы!")
        settings.bot.send_message(state, emoji.emojize(":party_popper:"))
        settings.bot.send_message(
            state,
            "Теперь бот полностью готов к работе. Просто перешлите или напишите сообщение, содержащее дату, и бот создаст вам событие.",
        )
    return RedirectResponse(f"https://t.me/{settings.bot.get_me().username}")


@app.get("/health")
async def healthceck():
    """
    Health check
    """
    return {"status": "ok"}
