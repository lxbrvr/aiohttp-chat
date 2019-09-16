import typing as t
import asyncio

from core.serialization.abc import BaseSerializer
from core.serialization.exceptions import ValidationError
from collections import abc as abc_collections

from core.serialization.typings import SerializedData, DeserializedData


class Serializer(BaseSerializer):
    async def serialize(self, data: t.Mapping[str, t.Any]) -> SerializedData:
        if not isinstance(data, abc_collections.Mapping):
            raise ValidationError(
                f'Expected a dictionary, but got {type(data).__name__}'
            )

        serialized_data = {}

        for field_name, field_obj in self.fields_map.items():
            if field_obj.deserialization_only:
                continue

            load_from = field_obj.load_from or field_name
            loaded_value = data.get(load_from, field_obj.value_for_missing)
            serialized_value = await field_obj.serialize(loaded_value)
            load_to = field_obj.load_to or field_name
            serialized_data[load_to] = serialized_value

        return serialized_data

    async def deserialize(
            self,
            data: t.Mapping[str, t.Any],
            partial: bool = False,
    ) -> DeserializedData:
        if not isinstance(data, abc_collections.Mapping):
            raise ValidationError(
                f'Expected a dictionary, but got {type(data).__name__}'
            )

        deserialized_data = {}

        for field_name, field_obj in self.fields_map.items():
            if field_obj.serialization_only:
                continue

            load_from = field_obj.load_from or field_name
            loaded_value = data.get(load_from, field_obj.value_for_missing)

            if not loaded_value and partial:
                continue

            if not loaded_value and field_obj.is_required and not field_obj.default:
                raise ValidationError(details=f'{load_from} field is required.')

            serialized_value = await field_obj.deserialize(loaded_value)
            load_to = field_obj.load_to or field_name
            deserialized_data[load_to] = serialized_value

        return deserialized_data

    async def serialize_many(
            self,
            objs: t.Sequence[t.Mapping[str, t.Any]],
    ) -> t.List[SerializedData]:
        return await asyncio.gather(*[self.serialize(o) for o in objs])

    async def deserialize_many(
            self,
            objs: t.Sequence[t.Mapping[str, t.Any]],
    ) -> t.List[DeserializedData]:
        return await asyncio.gather(*[self.deserialize(o) for o in objs])
