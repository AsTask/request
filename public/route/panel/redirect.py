from src.templating import Request, url_path, redirect, form, render_template

lang = {
    "ru": {
        "title": "Редирект",
        "route": {
            "panel": "Панель управления",
            "redirect": "Редирект",
        },
        "redirect_index": "Редирект на главную",
    },
}


async def response(request: Request) -> render_template:
    if "redirect" in form():
        return redirect(url=url_path("index"))
    return await render_template("route/panel/redirect.html", context={
        "lc": lang[request.lang],
    })
