import uuid
import datetime

from core.db import models
from core.utils import hash_password


class UserModel(models.Model):
    _id = models.Field(is_required=False)
    username = models.Field(default='')
    uuid = models.UUIDField(default=uuid.uuid4)
    password = models.Field()

    def set_password(self, password: str) -> None:
        self.password = hash_password(password)


class AccessTokenModel(models.Model):
    _id = models.Field(is_required=False)
    token = models.Field()
    user_uuid = models.UUIDField()
    created_at = models.Field(default=datetime.datetime.now)
    revoked_at = models.Field(is_required=False)
