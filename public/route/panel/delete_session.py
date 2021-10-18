from src.templating import Request, render_template

lang = {
    "ru": {
        "title": "Удалить сессию",
        "route": {
            "panel": "Панель управления",
            "delete_session": "Удалить сессию",
        },
    },
}


async def response(request: Request) -> render_template:
    request.session.clear()
    return await render_template("route/panel/delete_session.html", context={
        "lc": lang[request.lang],
    })
