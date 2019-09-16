import typing as t

from core.serialization.abc import BaseField, BaseSerializer
from core.serialization.exceptions import ValidationError
from core.serialization.typings import DeserializedData, SerializedData


class Field(BaseField):
    def __init__(
            self,
            *,
            load_from: str = None,
            load_to: str = None,
            value_for_missing: str = None,
            default: t.Any = None,
            is_required: bool = True,
            deserialization_only: bool = False,
            serialization_only: bool = False,
            **kwargs,
    ) -> None:
        self.load_from = load_from
        self.load_to = load_to
        self.value_for_missing = value_for_missing
        self.default = default
        self.is_required = is_required
        self.serialization_only = serialization_only
        self.deserialization_only = deserialization_only
        self.errors_map = []
        self.__dict__.update(kwargs)

    async def to_internal_type(self, value: t.Any) -> t.Any:
        return value

    async def to_representation(self, value: t.Any) -> t.Any:
        return value

    async def serialize(self, value: t.Any) -> t.Any:
        return await self.to_representation(value)

    async def deserialize(self, value: t.Any) -> t.Any:
        return await self.to_internal_type(value)


class TextField(Field):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def to_internal_type(self, value: t.Any) -> str:
        if not isinstance(value, (str, int, float)):
            raise ValidationError(details='')

        return str(value)

    async def to_representation(self, value: t.Any) -> str:
        return str(value)


class DateTimeField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def to_internal_type(self, value):
        pass

    async def to_representation(self, value):
        return value.isoformat()


class BooleanField(Field):
    TRUE_VALUES = [
        't', 'T',
        'y', 'Y', 'yes', 'YES',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    ]
    FALSE_VALUES = [
        'f', 'F',
        'n', 'N', 'no', 'NO',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    ]

    async def to_internal_type(self, value: t.Any) -> bool:
        if value in self.TRUE_VALUES:
            return True

        elif value in self.FALSE_VALUES:
            return False

        else:
            raise ValidationError('Must be a valid boolean')

    async def to_representation(self, value: t.Any) -> bool:
        if value in self.TRUE_VALUES:
            return True

        elif value in self.FALSE_VALUES:
            return False

        else:
            return bool(value)


class RefField(Field):
    def __init__(self, *, serializer_class: t.Type[BaseSerializer], **kwargs) -> None:
        super().__init__(**kwargs)
        self.serializer_class = serializer_class

        if not issubclass(serializer_class, BaseSerializer):
            raise ValidationError(details='')

    @property
    def serializer(self) -> BaseSerializer:
        return self.serializer_class(context=self.parent.context)

    async def to_internal_type(self, value: t.Any) -> DeserializedData:
        return await self.serializer.deserialize(value)

    async def to_representation(self, value: t.Any) -> SerializedData:
        return await self.serializer.serialize(value)


class UUIDField(Field):
    async def to_internal_type(self, value: t.Any) -> str:
        return str(value)

    async def to_representation(self, value: t.Any) -> str:
        return str(value)
