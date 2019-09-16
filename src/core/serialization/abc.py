import typing as t
import abc


class BaseField:
    @abc.abstractmethod
    async def serialize(self, value):
        pass

    @abc.abstractmethod
    async def deserialize(self, value):
        pass

    def _bind_to_serializer(self, name, serializer):
        self.parent = serializer
        self.name = name


class MetaSerializer(type):
    @classmethod
    def get_fields(mcs, attrs: t.Mapping[str, t.Any]) -> t.Dict[str, t.Type[BaseField]]:
        return {
            attr: obj
            for attr, obj in attrs.items()
            if isinstance(obj, BaseField)
        }

    def __new__(
            mcs,
            name: str,
            bases: t.Tuple[t.Type, ...],
            attrs: t.Dict[str, t.Any],
    ) -> type:
        cls = super().__new__(mcs, name, bases, attrs)
        cls.fields_map = mcs.get_fields(attrs)
        return cls


class _CombinedMetaClasses(abc.ABCMeta, MetaSerializer):
    pass


class BaseSerializer(metaclass=_CombinedMetaClasses):
    def __init__(self, context: t.Mapping[str, t.Any] = None) -> None:
        self.context = context or {}
        self._bind_fields()

    def _bind_fields(self) -> None:
        for fields_name, field_obj in self.fields_map.items():
            field_obj._bind_to_serializer(name=fields_name, serializer=self)

    @abc.abstractmethod
    async def serialize(self, data: t.Mapping[str, t.Any]):
        pass

    @abc.abstractmethod
    async def deserialize(self, data: t.Mapping[str, t.Any], partial=False):
        pass

    @abc.abstractmethod
    async def serialize_many(self, objs: t.Sequence[t.Mapping[str, t.Any]]):
        pass

    @abc.abstractmethod
    async def deserialize_many(self, objs: t.Sequence[t.Mapping[str, t.Any]]):
        pass
