from apps.messages.models import MessageModel
from core.db.query_sets import MongoDBQuerySet
from conf import settings


class MessagesQS(MongoDBQuerySet):
    collection_name = settings.MESSAGES_COLLECTION
    model_class = MessageModel
