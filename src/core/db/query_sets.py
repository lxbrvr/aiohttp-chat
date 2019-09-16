from __future__ import annotations

import typing as t
import abc

from motor import motor_asyncio
from pymongo import ReturnDocument

from core.db.models import Model


class QuerySet:
    """
    Interface for realizing of queries to the certain database.
    """

    model_class = None

    def __init__(self, *, db: motor_asyncio.AsyncIOMotorDatabase) -> None:
        self.db = db

    @abc.abstractmethod
    def __await__(self):
        pass

    @abc.abstractmethod
    async def all(self):
        """
        Returns all objects.
        """

        pass

    @abc.abstractmethod
    async def get_one(self, where):
        """
        Returns an one objects by filters.
        """

        pass

    @abc.abstractmethod
    async def filter(self, **kwargs):
        """
        Filters objects by passed parameters.
        """

        pass

    @abc.abstractmethod
    async def delete_one(self, where):
        """
        Deletes an one object by filter.
        """

        pass

    @abc.abstractmethod
    async def insert_one(self, model):
        """
        Inserts an one object to database.
        """

        pass

    @abc.abstractmethod
    async def insert_many(self, models):
        """
        Inserts many objects to database.
        """

        pass

    @abc.abstractmethod
    async def update_one(self, where, data):
        """
        Updates an one object.
        """

        pass

    @abc.abstractmethod
    async def count(self, **kw):
        """
        Counts and return the number of objects.
        """

        pass


class MongoDBQuerySet(QuerySet):
    """
    Implements the query set for mongo database.
    """

    collection_name = None

    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        self.cursor = None

    def __await__(self) -> t.Generator[t.Any, None, t.Any]:
        return self._fetch_all().__await__()

    async def _fetch_all(self, length: int = None) -> t.List[t.Type[Model]]:
        objs = await self.cursor.to_list(length=length)
        return list(map(lambda i: self.model_class(**i), objs))

    @property
    def collection(self) -> motor_asyncio.AsyncIOMotorCollection:
        """
        The shortcut for extraction of a collection object from a database.
        """

        return self.db[self.collection_name]

    def all(self) -> MongoDBQuerySet:
        """
        Returns all objects from collection.
        """

        self.cursor = self.collection.find()
        return self

    async def count(
            self, *,
            where: t.Mapping[str, t.Any] = None,
            limit: int = None,
            offset: int = None,
    ) -> int:
        """
        Returns number of documents in a collection.
        """

        extra = {}

        if limit:
            extra['limit'] = limit

        if offset:
            extra['offset'] = offset

        return await self.collection.count_documents(filter=where or {}, **extra)

    async def get_one(self, where: t.Mapping[str, t.Any]) -> t.Optional[Model]:
        """
        Finds an one document in a collection by passed filter and return it as model.
        """

        data = await self.collection.find_one(where)
        return self.model_class(**data) if data else None

    def filter(self, where: t.Mapping[str, t.Any]) -> MongoDBQuerySet:
        """
        Finds documents in a collection by passed
        filter and return them as models.
        """

        self.cursor = self.collection.find(where)
        return self

    async def update_one(
            self,
            where: t.Mapping[str, t.Any],
            data: t.Mapping[str, t.Any],
    ) -> t.Optional[t.Type[Model]]:
        """
        Updates a one document in a collection
        and returns it as model if it exists.
        """

        data = await self.collection.find_one_and_update(
            filter=where,
            update={'$set': data},
            return_document=ReturnDocument.AFTER,
        )
        return self.model_class(**data) if data else None

    async def delete_one(self, where: t.Mapping[str, t.Any]):
        """
        Deletes a one document in a collection found with filters.
        """

        return await self.collection.delete_one(where)

    async def insert_one(self, model: Model) -> Model:
        """
        Inserts a one document in a collection and returns it as model.
        """

        if not isinstance(model, Model):
            raise ValueError('insert_one method expects Model instance.')

        model_as_dict = model.as_dict

        if not model_as_dict.get('_id'):
            model_as_dict.pop('_id')

        result = await self.collection.insert_one(model_as_dict)
        return await self.get_one(where={'_id': result.inserted_id})

    async def insert_many(self, models: t.Sequence[Model]):
        """
        Inserts many documents in a collection and returns them as models.
        """

        for model in models:
            if not isinstance(model, Model):
                raise ValueError('insert_many method expects Model instances.')

        data = []

        for model in models:
            model_as_dict = model.as_dict

            if not model_as_dict.get('_id'):
                model_as_dict.pop('_id')

            data.append(model_as_dict)

        return await self.collection.insert_many(data)

    def offset(self, offset: int) -> MongoDBQuerySet:
        """
        Moves the mongodb cursor to defined offset value.
        """

        self.cursor = self.cursor.skip(offset)
        return self

    def limit(self, limit: int) -> MongoDBQuerySet:
        """
        Limits the documents in the cursor to defined limit value.
        """

        self.cursor = self.cursor.limit(limit)
        return self


