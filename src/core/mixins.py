import typing as t

from aiohttp.web_exceptions import HTTPNotFound

from core.db.models import Model
from core.db.query_sets import QuerySet


class ModelObjectMixin:
    """
    Mixin class for using in ApiView.
    Contains the logic for working with certain objects from database.
    """

    query_set_class: t.Type[QuerySet] = None
    url_param: str = None
    lookup_field: str = None

    async def check_object_permissions(self, obj: Model) -> None:
        for permission in self.get_permissions():
            if not await permission.has_object_permission(self.request, obj):
                self.permission_denied()

    def get_url_param_value(self) -> str:
        """
        Extracts a part of a url path which contains object identifier.
        If it doesn't exists then raises 404 error.
        """

        param_value = self.request.match_info.get(self.url_param)

        if not param_value:
            raise HTTPNotFound()

        return param_value

    async def get_object(self) -> Model:
        """
        Finds an object in a database based on url
        path and returns it if exists.
        """

        return (
            await
            self.query_set_class(db=self.db)
            .get_one(where={self.lookup_field: self.get_url_param_value()})
        )

    async def _get_object_or_404(self) -> Model:
        obj = await self.get_object()

        if not obj:
            raise HTTPNotFound()

        return obj
