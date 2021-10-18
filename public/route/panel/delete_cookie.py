from src.templating import Request, delete_cookie, render_template

lang = {
    "ru": {
        "title": "Удалить куку",
        "route": {
            "panel": "Панель управления",
            "delete_cookie": "Удалить куку",
        },
    },
}


async def response(request: Request) -> render_template:
    delete_cookie(key="key")
    return await render_template("route/panel/delete_cookie.html", context={
        "lc": lang[request.lang],
    })
