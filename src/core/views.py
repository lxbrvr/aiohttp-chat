import typing as t
from json import JSONDecodeError
from http import HTTPStatus

from motor import motor_asyncio

from aiohttp import hdrs
from aiohttp.abc import AbstractView
from aiohttp.web_exceptions import (
    HTTPMethodNotAllowed,
    HTTPException,
    HTTPUnauthorized,
    HTTPForbidden,
)
from aiohttp.web_response import Response, json_response

from core.authentication import BaseAuthentication
from core.db.models import Model
from core.db.query_sets import QuerySet
from core.mixins import ModelObjectMixin
from core.paginators import LimitOffsetPaginator, PaginatorBase
from core.permissions import BasePermission
from core.serialization.abc import BaseSerializer
from core.serialization.exceptions import ValidationError
from core.serialization.typings import DeserializedData, SerializedData


class ApiView(AbstractView):
    authentication_classes: t.Sequence[t.Type[BaseAuthentication]] = []
    serializer_class: t.Type[BaseSerializer] = None
    permission_classes: t.Sequence[t.Type[BasePermission]] = []

    def __await__(self) -> t.Generator[t.Any, None, t.Any]:
        return self.dispatch().__await__()

    @property
    def db(self) -> motor_asyncio.AsyncIOMotorDatabase:
        """
        The shortcut for extraction a database from request.
        """

        return self.request.app.mongo

    def get_handler_or_raise_405(self) -> t.Callable[[], t.Coroutine[t.Any, t.Any, Response]]:
        """
        Finds and returns the handler in current class for requested method.
        Otherwise raises 405 response.
        """

        handler = getattr(self, self.request.method.lower(), None)

        if not handler:
            raise HTTPMethodNotAllowed(
                method=self.request.method,
                allowed_methods=self.get_allowed_methods(),
            )

        return handler

    def get_allowed_methods(self) -> t.Set[str]:
        """
        Returns allowed methods for requests.
        """

        return {m for m in hdrs.METH_ALL if hasattr(self, m.lower())}

    async def dispatch(self) -> Response:
        """
        The entry point for every request.
        """

        handler = self.get_handler_or_raise_405()
        await self.perform_authentication()
        await self.check_permissions()

        try:
            response = await handler()
        except HTTPException as e:
            raise e
        except JSONDecodeError as e:
            return json_response(
                status=HTTPStatus.BAD_REQUEST.value,
                data={
                    'code': 'internal_error',
                    'message': str(e),
                },
            )
        except Exception:
            return json_response(
                status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                data={
                    'code': 'internal_error',
                    'message': 'Internal error.',
                },
            )

        return response

    def get_permissions(self) -> t.List[BasePermission]:
        """
        Initiates permission classes and returns them.
        """

        return [permission() for permission in self.permission_classes]

    async def check_permissions(self) -> None:
        for permission in self.get_permissions():
            if not await permission.has_permission(self.request):
                self.permission_denied()

    def permission_denied(self) -> None:
        if self.get_authenticators() and not self.request.is_authenticated:
            raise HTTPUnauthorized()
        raise HTTPForbidden()

    def get_authenticators(self) -> t.List[BaseAuthentication]:
        """
        Initiates authentication classes and returns them.
        """

        return [auth() for auth in self.authentication_classes]

    async def perform_authentication(self) -> None:
        """
        Tries authenticate a request user.
        Assigns the user object into request object
        if the authentication process is successful.
        """

        for authenticator in self.get_authenticators():
            user = await authenticator.authenticate(self.request)
            if user:
                self.request.is_authenticated = True
                self.request.user = user
                return

        self.request.is_authenticated = False
        self.request.user = None

    def get_serializer_context(self) -> t.Dict[str, t.Any]:
        """
        Forms the context that will be passed to serializer.
        """

        return {'request': self.request}

    def get_serializer(self) -> BaseSerializer:
        """
        Initiates a serializer and returns it.
        """

        return self.serializer_class(context=self.get_serializer_context())


class ListApiView(ApiView):
    """
    The view helper for requesting of list of objects.
    """

    paginator_class: t.Type[PaginatorBase] = LimitOffsetPaginator
    query_set_class: t.Type[QuerySet] = None

    async def get_objects(self) -> t.Awaitable:
        """
        Returns list of objects that will be processed.
        """

        return self.query_set_class(db=self.db).all()

    async def paginate(self, objects: t) -> t.List:
        if not self.paginator_class:
            return objects

        return await self.paginator_class().paginate(
            objects=objects,
            request=self.request,
        )

    async def get(self) -> Response:
        filtered_objects = await self.get_objects()
        paginated_objects = await self.paginate(filtered_objects)
        objects_as_dict = [f.as_dict for f in await paginated_objects]
        serialized_objects = await self.get_serializer().serialize_many(objects_as_dict)

        return json_response(
            data=serialized_objects,
            status=HTTPStatus.OK.value,
        )


class DetailApiView(ModelObjectMixin, ApiView):
    """
    The view helper for requesting of certain objects.
    """

    async def get(self) -> Response:
        obj = await self._get_object_or_404()
        await self.check_object_permissions(obj)

        return json_response(
            data=await self.get_serializer().serialize(obj.as_dict),
            status=HTTPStatus.OK.value,
        )


class CreateApiView(ApiView):
    """
    The view helper for creation of objects in database.
    """

    query_set_class: t.Type[QuerySet] = None

    async def deserialize(self, data):
        """
        Deserializes the data from the request and returns it as deserialized.
        """

        return await self.get_serializer().deserialize(data)

    async def serialize(self, data):
        """
        Serializes the data from the request and returns it as serialized.
        """

        return await self.get_serializer().serialize(data)

    async def post_serialize(self, serialized_data):
        """
        Override this method if you need execute code after serialization.
        """

        return serialized_data

    async def post(self):
        try:
            request_data = await self.request.json()
            deserialized_object = await self.deserialize(request_data)
            model = await self.init_model(deserialized_object)
            created_object = await self.create(model)
        except ValidationError as e:
            return json_response(
                data={'errors': e.details},
                status=HTTPStatus.BAD_REQUEST.value,
            )

        serialized_object = await self.serialize(created_object.as_dict)
        serialized_object = await self.post_serialize(serialized_object)

        return json_response(
            data=serialized_object,
            status=HTTPStatus.CREATED.value,
        )

    async def init_model(self, deserialized_object: DeserializedData) -> Model:
        """
        Initiates a model object with deserialized data.
        """

        return self.query_set_class.model_class(**deserialized_object)

    async def create(self, model: Model) -> Model:
        """
        Initiates the process of object insertion to database.
        """

        return await self.query_set_class(db=self.db).insert_one(model)


class DestroyApiView(ModelObjectMixin, ApiView):
    """
    The view helper for deletion of objects.
    """

    async def destroy(self, model: Model) -> None:
        """
        Initiates the process of object deletion from database.
        """

        await self.query_set_class(db=self.db).delete_one(
            where={self.lookup_field: getattr(model, self.lookup_field)},
        )

    async def delete(self) -> Response:
        obj = await self._get_object_or_404()
        await self.check_object_permissions(obj)
        await self.destroy(obj)

        return json_response(
            data={},
            status=HTTPStatus.NO_CONTENT.value,
        )


class UpdateApiView(ModelObjectMixin, ApiView):
    """
    The view helper for PUT-updating of objects.
    """

    async def deserialize(
            self,
            data: t.Mapping[str, t.Any],
            partial: bool = False
    ) -> DeserializedData:
        """
        Deserializes the data from the request and returns it as deserialized.
        """

        return await self.get_serializer().deserialize(data=data, partial=partial)

    async def serialize(self, data: t.Mapping[str, t.Any]) -> SerializedData:
        """
        Serializes the data from the request and returns it as serialized.
        """

        return await self.get_serializer().serialize(data)

    async def post_serialize(self, serialized_data: SerializedData) -> SerializedData:
        """
        Override this method if you need execute code after serialization.
        """

        return serialized_data

    async def update(self, obj: Model, data: t.Mapping[str, t.Any]) -> Model:
        """
        Initiates the process of object updating in database.
        """

        return await self.query_set_class(db=self.db).update_one(
            where={self.lookup_field: getattr(obj, self.lookup_field)},
            data=data,
        )

    async def put(self, partial: bool = False) -> Response:
        obj = await self._get_object_or_404()
        await self.check_object_permissions(obj)

        try:
            request_data = await self.request.json()
            deserialized_object = await self.deserialize(data=request_data, partial=partial)
            updated_object = await self.update(obj, deserialized_object)
        except ValidationError as e:
            return json_response(
                data={'errors': e.details},
                status=HTTPStatus.BAD_REQUEST.value,
            )

        serialized_object = await self.serialize(updated_object.as_dict)
        serialized_object = await self.post_serialize(serialized_object)

        return json_response(
            data=serialized_object,
            status=HTTPStatus.OK.value,
        )


class PatchApiView(UpdateApiView):
    """
    The view helper for PATCH-updating of objects.
    """

    async def patch(self) -> Response:
        return await self.put(partial=True)
