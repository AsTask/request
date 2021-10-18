from src.templating import Request, render_template
from instance.utils import generate_secret_key

lang = {
    "ru": {
        "title": "Установить сессию",
        "route": {
            "panel": "Панель управления",
            "set_session": "Установить сессию",
        },
    },
}


async def response(request: Request) -> render_template:
    request.session.update({"key": generate_secret_key(length=32)})
    return await render_template("route/panel/set_session.html", context={
        "lc": lang[request.lang],
    })
