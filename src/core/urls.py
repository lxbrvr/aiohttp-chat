import typing as t
import importlib

import aiohttp_cors

from conf import settings


class URLPattern:
    """
    The class for more convenient way construction of url patterns.
    """

    def __init__(self, method: str, path: str, handler, name: str = None) -> None:
        self.method = method
        self.path = path
        self.handler = handler
        self.name = name


def setup_routes(app: 'Application', url_paths: t.Sequence[str]) -> None:
    """
    Collects url patterns and appends them to Application.
    """

    patterns_list = [importlib.import_module(u).patterns for u in url_paths]

    for url_patterns in patterns_list:
        if not isinstance(url_patterns, (list, tuple)):
            raise RuntimeError('url pattern collection must be list or tuple.')

        if not url_patterns:
            continue

        for url_pattern in url_patterns:
            if not isinstance(url_pattern, URLPattern):
                raise RuntimeError(
                    'url pattern collection must be '
                    'URLPattern instance.'
                )

            app.router.add_route(
                method=url_pattern.method,
                path=url_pattern.path,
                handler=url_pattern.handler,
                name=url_pattern.name,
            )


def setup_cors(app: 'Application') -> None:
    """
    Adds CORS headers to all routes.
    """

    cors = aiohttp_cors.setup(app)

    for route in list(app.router.routes()):
        cors.add(
            routing_entity=route,
            config={
                origin: aiohttp_cors.ResourceOptions(
                    allow_credentials=settings.CORS_ALLOWED_CREDENTIALS,
                    expose_headers=settings.CORS_ALLOWED_METHODS,
                    allow_headers=settings.CORS_ALLOWED_HEADERS,
                    allow_methods=settings.CORS_ALLOWED_METHODS,
                ) for origin in settings.CORS_ALLOWED_ORIGINS
            }
        )


url = URLPattern
