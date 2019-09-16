import typing as t
import enum

from aiohttp.web_request import Request
from aiohttp.abc import AbstractView
from aiohttp import web

from core.serialization.typings import SerializedData
from core.authentication import TokenAuthentication


class ChannelActions(str, enum.Enum):
    ADD_MESSAGE = 'add_message'
    UPDATE_MESSAGE = 'update_message'
    DELETE_MESSAGE = 'delete_message'


class WSCHatChanel:
    def __init__(self, request: Request) -> None:
        self.request = request

    async def send(self, action: ChannelActions, data: SerializedData) -> None:
        for ws_conn in self.request.app.ws_conns:
            await ws_conn.send_json({'action': action, 'data': data})

    async def add_message(self, data: SerializedData) -> None:
        await self.send(action=ChannelActions.ADD_MESSAGE, data=data)

    async def update_message(self, data: SerializedData) -> None:
        await self.send(action=ChannelActions.UPDATE_MESSAGE, data=data)

    async def delete_message(self, data: SerializedData) -> None:
        await self.send(action=ChannelActions.DELETE_MESSAGE, data=data)


class WSView(AbstractView):
    def __await__(self) -> t.Generator[t.Any, None, t.Any]:
        return self.process().__await__()

    async def init_ws(self) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        return ws

    async def connect_ws(self, ws: web.WebSocketResponse) -> None:
        self.request.app.ws_conns.append(ws)

    async def disconnect_ws(self, ws: web.WebSocketResponse) -> None:
        self.request.app.ws_conns.pop(ws)

    async def perform_authentication(self, ws: web.WebSocketResponse) -> None:
        user = await TokenAuthentication().authenticate(self.request)

        if not user:
            await ws.close()

        self.request.user = user

    async def listen_to_ws(self, ws: web.WebSocketResponse) -> None:
        async for _ in ws:
            pass

    async def process(self) -> web.WebSocketResponse:
        current_ws = await self.init_ws()
        await self.perform_authentication(current_ws)
        await self.connect_ws(current_ws)
        await self.listen_to_ws(current_ws)
        await self.disconnect_ws(current_ws)
        return current_ws
