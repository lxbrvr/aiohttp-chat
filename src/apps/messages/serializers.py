from apps.users.query_sets import UsersQS
from apps.users.serializers import UserSerializer
from core.serialization.serializers import Serializer
from core.serialization import fields
from core.serialization.typings import SerializedData, DeserializedData


class MessageSerializer(Serializer):
    id = fields.UUIDField(load_from='uuid', serialization_only=True)
    text = fields.TextField(min_length=1, max_length=100)
    created_at = fields.DateTimeField(serialization_only=True)
    author = fields.RefField(serializer_class=UserSerializer, serialization_only=True)

    async def serialize(self, data: SerializedData) -> SerializedData:
        db = self.context.get('request').app.mongo
        author = await UsersQS(db=db).get_by_uuid(data['author_uuid'])
        data['author'] = author.as_dict
        serialized_data = await super().serialize(data)
        return serialized_data

    async def deserialize(
            self,
            data: DeserializedData,
            partial: bool = False,
    ) -> DeserializedData:
        deserialized_data = await super().deserialize(data, partial=partial)
        deserialized_data['author_uuid'] = self.context.get('request').user.uuid
        return deserialized_data

