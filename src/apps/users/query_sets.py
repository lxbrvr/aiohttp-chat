import typing as t

from apps.users.models import UserModel, AccessTokenModel
from conf import settings
from core.db.query_sets import MongoDBQuerySet


class UsersQS(MongoDBQuerySet):
    collection_name = settings.USERS_COLLECTION
    model_class = UserModel

    async def get_by_username(self, username: str) -> t.Optional[UserModel]:
        return await self.get_one(where={'username': username})

    async def get_by_uuid(self, uuid: str) -> t.Optional[UserModel]:
        return await self.get_one(where={'uuid': uuid})


class AccessTokenQS(MongoDBQuerySet):
    collection_name = settings.ACCESS_TOKEN_COLLECTION
    model_class = AccessTokenModel
