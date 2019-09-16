from __future__ import annotations

import typing as t
from uuid import UUID


class Field:
    """
    The descriptor for using in Model classes.
    The descriptor takes different parameters for initialization and
    validation of certain arguments passed to Model class.
    """

    def __init__(
            self,
            default: t.Optional[t.Any] = None,
            is_required: bool = True,
    ) -> None:
        self.default = default
        self.is_required = is_required
        self.name = None

    def __set_name__(self, owner: 'Model', name: str) -> None:
        self.name = name

    def __get__(self, instance: Field, owner: 'Model') -> t.Any:
        return instance.__dict__.get(self.name, self.get_default())

    def __set__(self, instance: Field, value: t.Any) -> None:
        if not value and self.is_required and not self.get_default():
            raise ValueError(f'{self.name} is required')

        value = self.get_default() if value is None else value
        value = self.prepare_value(value)

        instance.__dict__[self.name] = value

    def prepare_value(self, value: t.Any) -> t.Any:
        """
        Override this method if need to prepare a value before setting.
        """

        return value

    def get_default(self) -> t.Any:
        if self.default is not None:
            if callable(self.default):
                return self.default()
            return self.default
        return None


class UUIDField(Field):
    def prepare_value(self, value: t.Union[str, UUID]) -> str:
        return str(value)


class ModelMetaclass(type):
    @classmethod
    def get_fields(mcs, attrs: t.Mapping[str, t.Any]) -> t.Dict[str, Field]:
        """
        Collects and returns Field classes defined in Model.
        """

        return {
            attr: obj
            for attr, obj in attrs.items()
            if isinstance(obj, Field)
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


class Model(metaclass=ModelMetaclass):
    """
    The model class for storing different values.
    """

    def __init__(self, **kw) -> None:
        for field_name in self.fields_map.keys():
            field_value = kw.get(field_name, None)
            setattr(self, field_name, field_value)

    @property
    def as_dict(self) -> t.Dict[str, t.Any]:
        """
        Collects field values, transforms it to dict and returns.
        """

        return {k: getattr(self, k, None) for k in self.fields_map.keys()}
