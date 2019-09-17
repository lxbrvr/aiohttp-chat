from __future__ import annotations

import uvloop
from motor import motor_asyncio

from aiohttp import web, WSCloseCode

from conf import settings
from core.urls import setup_routes, setup_cors


class Application(web.Application):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.ws_conns = []
        self.mongo_client = None

        self.setup_routes()
        self.setup_cors()

        self.on_startup.append(self.startup_mongodb)
        self.on_cleanup.append(self.cleanup_mongodb)
        self.on_cleanup.append(self.cleanup_ws_conns)

    def setup_routes(self) -> None:
        setup_routes(app=self, url_paths=settings.URLS)

    def setup_cors(self) -> None:
        setup_cors(self)

    async def startup_mongodb(self, app: Application) -> None:
        app.mongo_client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
        app.mongo = app.mongo_client.get_database()

    async def cleanup_mongodb(self, app: Application) -> None:
        app.mongo_client.close()

    async def cleanup_ws_conns(self, app: Application) -> None:
        for ws in app.ws_conns:
            await ws.close(
                code=WSCloseCode.GOING_AWAY,
                message='Server shutdown.',
            )


def run_app(port: int, **kwargs) -> None:
    uvloop.install()
    web.run_app(app=Application(), host='0.0.0.0', port=port, **kwargs)
