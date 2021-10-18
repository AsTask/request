__all__ = [
    "set_header", "set_cookie", "delete_cookie", "static", "url_path", "redirect", "form", "render_template",
    "Request", "HttpBase",
]

import typing
import os
from importlib import import_module

from starlette.requests import Request as _Request
from starlette.responses import Response, RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.background import BackgroundTask
from starlette.datastructures import URL

from instance.const import PUBLIC_PATH
from instance.utils import pack_path
from src import language

_request: _Request
_header: typing.Dict[str, str]
_cookie: typing.List[dict]
_form: typing.Dict[str, typing.Any]
_path: str
_list: typing.List[str]
_dict: typing.Dict[str, typing.Any]

_module = import_module(__name__)


def set_header(key: str, value: str = "") -> None:
    Http.get(name="header").update({key: value})


def set_cookie(
        key: str,
        value: str = "",
        max_age: int = None,
        expires: int = None,
        path: str = "/",
        domain: str = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: str = "lax",
) -> None:
    cookie, cookie["key"], cookie["value"] = {}, key, value
    if max_age is not None:
        cookie["max_age"] = max_age
    if expires is not None:
        cookie["expires"] = expires
    if path is not None:
        cookie["path"] = path
    if domain is not None:
        cookie["domain"] = domain
    if secure:
        cookie["secure"] = True
    if httponly:
        cookie["httponly"] = True
    if samesite is not None:
        assert \
            samesite.lower() in (
                "strict", "lax", "none"
            ), "samesite должен быть 'strict', 'lax' либо 'none'"
        cookie["samesite"] = samesite
    Http.get(name="cookie").append(cookie)


def delete_cookie(key: str, path: str = "/", domain: str = None) -> None:
    Http.get(name="cookie").append({"key": key, "expires": 0, "max_age": 0, "path": path, "domain": domain})


def redirect(
        url: str,
        status_code: int = 307,
        headers: dict = None,
        background: BackgroundTask = None,
) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code, headers=headers, background=background)


def form() -> typing.Dict[str, typing.Any]:
    return Http.get(name="form") if Http.has(name="form") else {}


def static(name: str, **path_params: typing.Any) -> str:
    router = Http.get(name="request").scope["router"]
    return router.url_path_for(name=name, **path_params)


def url_path(name: str, **path_params: typing.Any) -> str:
    router = Http.get(name="request").scope["router"]
    return router.url_path_for(name=name, **path_params)


async def render_template(
        name: str,
        context: dict = None,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTask = None,
) -> Jinja2Templates.TemplateResponse:
    def template_assert(model_dict) -> None:
        for key in model_dict:
            assert \
                key not in (model_list := Http.get(name="list")), \
                f"{pack_path(__file__)} в классе Jinja: ключ '{key}' уже имеется в словаре шаблона {model_list}"
            model_list.append(key)

    template = Jinja2Templates(directory=os.path.join(
        Http.get(name="path") if Http.has(name="path") else PUBLIC_PATH, "templates"
    ))
    template.env.globals.update({
        "static": static,
        "url_path": url_path,
    })
    Http.set(name="list", value=[*[key for key in template.env.globals], "request"])
    if Http.has(name="dict"):
        template_assert(model_dict=(env := Http.get(name="dict")))
        for key in env:
            template.env.globals.update({key: env[key]})
    env = {} if context is None else context
    template_assert(model_dict=env)
    return template.TemplateResponse(
        name=name,
        context=env | {"request": Http.get(name="request")},
        status_code=status_code,
        headers=headers,
        media_type=media_type,
        background=background,
    )


class Request:
    __slots__ = ["lang", "main", "current", "url", "path", "method", "headers", "cookies", "session"]
    lang: str
    main: str
    current: str
    url: URL
    path: dict
    method: str
    headers: typing.Dict[str, str]
    cookies: typing.Dict[str, str]
    session: dict


class Http(Request):
    @classmethod
    def set(cls, name: str, value: typing.Any) -> None:
        setattr(_module, f"_{name}", value)

    @classmethod
    def has(cls, name: str) -> bool:
        return hasattr(_module, f"_{name}")

    @classmethod
    def get(cls, name: str) -> typing.Any:
        return getattr(_module, f"_{name}")

    def __init__(self, request: _Request) -> None:
        self.set(name="request", value=request)
        self.set(name="header", value={})
        self.set(name="cookie", value=[])
        self.set(name="form", value={})

    async def initial(self, template: str, main: str, name: str = None) -> None:
        if (request := self.get(name="request")).method == "POST":
            self.get(name="form").update({item[0]: item[1] for item in (await request.form()).items()})
        current, _ = (split := os.path.splitext(request.url.path))[0], split[1]
        for item in [
            ("lang", language.lang(template=template)),
            ("main", main),
            ("current", current),
            ("url", request.url),
            ("path", request.path_params),
            ("method", request.method),
            ("headers", request.headers),
            ("cookies", request.cookies),
            ("session", request.session),
        ]:
            setattr(Request, *item)
        getattr(self, f"{template}_env")(name="index" if name is None else name)

    async def not_found(self, template: str) -> Response:
        name, lc = f"template/{template}/not_found.html", language.base["not_found"][self.lang]
        return self.headers(response=await render_template(name=name, context={"lc": lc}, status_code=404))

    def base_env(self, name: str) -> None:
        self.set(name="path", value=PUBLIC_PATH)
        self.set(name="dict", value={
            "lang": self.lang,
            "lt": language.base[name][self.lang],
            "main": self.main == self.current,
            "href_main": self.main,
        })

    def error_module(self) -> tuple:
        error, path = True, os.path.join(PUBLIC_PATH, 'route', (
            route := current if (current := self.current[1:]) else "index"
        ).replace('/', os.sep))
        if os.path.isdir(path):
            error, route = False, f"{route}.__init__"
        else:
            if os.path.isfile(f"{path}.py"):
                error = False
        return error, f"public.route.{route.replace('/', '.')}"

    def headers(self, response: Response) -> Response:
        if self.has(name="header"):
            for key in (header := self.get(name="header")):
                response.headers[key] = header[key]
        if self.has(name="cookie"):
            for item in self.get(name="cookie"):
                response.set_cookie(**item)
        return response


class HttpBase(Http):
    def __init__(self, request: _Request) -> None:
        super().__init__(request=request)

    async def response(self) -> typing.Union[render_template, Response]:
        await self.initial(template="base", main=url_path("index"))
        error, module = self.error_module()
        if error:
            return await self.not_found(template="base")
        return self.headers(response=await getattr(import_module(module), "response")(request=Request))

    async def error(self, status_code: int) -> Response:
        if not_found := status_code == 404:
            await self.initial(template="base", main=url_path("index"))
            self.get(name="dict")["lc"] = language.base["not_found"][self.lang]
        else:
            self.get(name="dict")["lt"] = language.base["server_error"][self.lang]
        name = f"template/base/{'not_found' if not_found else 'server_error'}.html"
        return self.headers(response=await render_template(name=name, status_code=status_code))
