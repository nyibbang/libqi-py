from typing import Any
from functools import total_ordering


class MetaObject:
    pass


@total_ordering
class Object:
    def __init__(self, uid: bytes, meta_object: MetaObject) -> None:
        self.uid = uid
        self.meta_object = meta_object

    def _is_valid_operand(self, other: Any) -> bool:
        return isinstance(other, Object)

    def __eq__(self, other: Any) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.uid == other.uid

    def __lt__(self, other: Any) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.uid < other.uid

    def __bool__(self) -> bool:
        return self.isValid()

    def isValid(self) -> bool:
        return self.uid is not None

    def call(self, funcName, *args, **kwargs):
        raise NotImplementedError()

    def metaObject(self) -> MetaObject:
        return self.meta_object
