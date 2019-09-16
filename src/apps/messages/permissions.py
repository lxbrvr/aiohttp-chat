from aiohttp.web_request import Request

from apps.messages.models import MessageModel
from core.permissions import BasePermission


class IsMessageOwner(BasePermission):
    async def has_object_permission(self, request: Request, obj: MessageModel) -> bool:
        return request.user.uuid == obj.author_uuid
