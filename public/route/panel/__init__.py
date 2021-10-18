from src.templating import Request, render_template

lang = {
    "ru": {
        "title": "Панель управления",
        "route": "Панель управления",
        "set_cookie": "Установить куку",
        "delete_cookie": "Удалить куку",
        "set_session": "Установить сессию",
        "delete_session": "Удалить сессию",
        "redirect": "Редирект",
    },
}


async def response(request: Request) -> render_template:
    request.session.update()
    return await render_template("route/panel/index.html", context={
        "lc": lang[request.lang],
        "cookies_key": cookies if (cookies := request.cookies.get("key")) is None else "key",
        "cookies_value": cookies,
        "session_key": session if (session := request.session.get("key")) is None else "key",
        "session_value": session,
    })
