import typing as t

from apps.users.query_sets import UsersQS
from conf import settings
from core.serialization.exceptions import ValidationError
from core.serialization.serializers import Serializer
from core.serialization import fields
from core.serialization.typings import DeserializedData
from core.utils import verify_password, hash_password, generate_jwt


class UserSerializer(Serializer):
    id = fields.UUIDField(load_from='uuid', serialization_only=True)
    username = fields.TextField()
    password = fields.TextField(deserialization_only=True)

    async def deserialize(self, data: t.Dict[str, t.Any], partial: bool=False) -> DeserializedData:
        deserialized_data = await super().deserialize(data, partial=partial)

        username = deserialized_data['username']
        db = self.context['request'].app.mongo
        user = await UsersQS(db=db).get_by_username(username)

        if user:
            raise ValidationError('This username is already in use.')

        hashed_password = hash_password(deserialized_data['password'])
        deserialized_data['password'] = hashed_password
        return deserialized_data


class AccessTokenSerializer(Serializer):
    username = fields.TextField(deserialization_only=True)
    password = fields.TextField(deserialization_only=True)
    access_token = fields.TextField(serialization_only=True, load_from='token')

    async def deserialize(self, data: t.Dict[str, t.Any], partial: bool=False) -> DeserializedData:
        deserialized_data = await super().deserialize(data, partial)
        username = deserialized_data['username']
        raw_password = deserialized_data['password']
        db = self.context['request'].app.mongo
        user = await UsersQS(db=db).get_by_username(username)

        if not user:
            raise ValidationError(
                'Wrong credentials.'
            )

        is_correct_password = verify_password(raw_password, user.password)

        if not is_correct_password:
            raise ValidationError('Wrong credentials.')

        deserialized_data.update({
            'user_uuid': user.uuid,
            'token': generate_jwt(
                exp_in_secs=settings.JWT_EXP_SECONDS,
                secret_key=settings.SECRET_KEY,
                payload={'user_id': user.uuid},
            ),
        })

        return deserialized_data
