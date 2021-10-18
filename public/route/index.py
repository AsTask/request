from src.templating import Request, render_template

lang = {
    "ru": {
        "title": "Главная страница",
        "route": "Главная страница",
        "not_found": "Страница не найдена",
        "server_error": "Ошибка сервера",
    },
}


async def response(request: Request) -> render_template:
    return await render_template("route/index.html", context={
        "lc": lang[request.lang],
    })
