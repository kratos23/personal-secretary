# Personal Secretary Bot
## Установка
Personal Secretary Bot работает только на дистрибутивах Linux

1. Убедитесь, что у вас установлен Python3.7 и pip3
2. [Установите poetry](https://python-poetry.org/docs/#installation)
3. Склонируйте репозиторий и перейдите в папку с кодом
4. Убедитесь, что poetry использует для окружения Python3.7
    ```bash
    $ poetry env use <YOUR_PYTHON3.7_PATH> 
    ```
5. Установите зависимости
    ```bash
    $ poetry install --no-dev
    ```
    если вам необходимы различные инстурменты разработки, то уберите `--no-dev`
6. Активируйте виртуальное окружение
    ```bash
    $ poetry shell
    ```
7. Установите модуль ner_ontonotes_bert_mult для deeppavlov
    ```bash
    $ python -m deeppavlov install ner_ontonotes_bert_mult
    ```
8. Теперь необоходимо обновить зависимости, так как из-за [конфликта зависимостей](https://github.com/deepmipt/DeepPavlov/issues/1553) deeppavlov переписывает указанные в проекте зависимости
    ```bash
    $ poetry update
    ```
9. Скопируйте `.env.example`, переименуйте его в `.env` и заполните все поля в нем необходимыми данными
    ```bash
    $ cp .env.example .env && vim .env
    ```
10. Инициализируйте БД
    ```bash
    $ ./tools/init_db.py
    ```
10. [Скачайте JSON с данными вашего Google приложения](https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name-.) и сохраните его в корневой папке проекта с названием `client_secret.json`
11. Чтобы запустить бота
    ```bash
    $ poetry run bot
    ```
12. Чтобы запустить обработчик callback'ов Google
    ```bash
    $ uvicorn src.callback:app --proxy-headers --host localhost --port 800 
    ```