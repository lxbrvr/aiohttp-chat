import abc
import typing as t

from aiohttp.web_request import Request

from core.db.query_sets import QuerySet


class PaginatorBase(metaclass=abc.ABCMeta):
    """
    The base pagination interface for using in ApiView.
    """

    def __init__(self) -> None:
        self.count = 0

    @abc.abstractmethod
    def paginate(self, objects: QuerySet, request: Request):
        """
        The entry point for realizing of the pagination.
        """

        pass


class LimitOffsetPaginator(PaginatorBase):
    limit_query_param: str = 'limit'
    offset_query_param: str = 'offset'
    default_limit: int = 20
    max_limit: int = 100

    @staticmethod
    def _normalize_number(number: t.Union[str, int, float]) -> t.Optional[int]:
        try:
            number = int(number)
            return abs(number)
        except (TypeError, ValueError):
            pass
        return

    async def paginate(self, objects: t.Any, request: Request) -> t.List[t.Any]:
        self.count = await self.get_count(objects)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)

        if self.offset > self.count or self.count == 0:
            return []

        if not self.limit:
            return objects

        return self.get_slice(objects, self.offset, self.limit)

    def get_slice(self, objects: t.Any, offset: int, limit: int):
        return objects.offset(offset).limit(limit)

    async def get_count(self, objects: t.Any) -> int:
        return await objects.count()

    def get_limit(self, request: Request) -> int:
        limit = request.query.get(self.limit_query_param, None)
        return min(self._normalize_number(limit) or self.default_limit, self.max_limit)

    def get_offset(self, request: Request) -> int:
        """
        Normalizes found offset value from query string and returns it

        :param request: request object
        :return: normalized number

        """

        offset = request.query.get(self.offset_query_param, 0)
        return self._normalize_number(offset) or 0
