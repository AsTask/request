from instance.data import get_object

base = {
    "index": {
        "ru": {
            "sign_in": "Войти",
        },
    },
    "not_found": {
        "ru": {
            "title": "Ошибка 404",
            "content": "Ошибка 404. Страница не найдена",
        },
    },
    "server_error": {
        "ru": {
            "title": "Ошибка 500",
            "header": "500. Ошибка сервера.",
            "content": "Сервер упал по данному запросу.",
            "back": "Вернуться на сайт",
        },
    },
}


def lang(template: str) -> str:
    return get_object("language")[template]["lang"]
