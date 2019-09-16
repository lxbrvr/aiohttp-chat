import uuid
import datetime

from core.db import models


class MessageModel(models.Model):
    _id = models.Field(is_required=False)
    uuid = models.UUIDField(default=uuid.uuid4)
    text = models.Field(default='')
    author_uuid = models.UUIDField()
    created_at = models.Field(default=datetime.datetime.now)
    updated_at = models.Field(is_required=False)
