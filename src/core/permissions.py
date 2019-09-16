from aiohttp.web_request import Request

from core.db.models import Model


class BasePermission:
    """
    The base permission interface for using in ApiView.
    """

    async def has_permission(self, request: Request) -> bool:
        """
        Checks user permissions to certain endpoint in ApiVIew.
        """

        return True

    async def has_object_permission(self, request: Request, obj: Model) -> bool:
        """
        Checks the user permissions for accessing to certain model object
        """

        return True


class IsAuthenticated(BasePermission):
    """
    Checks that a request user is authenticated.
    """

    async def has_permission(self, request: Request) -> bool:
        return request.user and request.is_authenticated




