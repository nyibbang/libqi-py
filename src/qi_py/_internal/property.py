from typing import Callable, Generic, TypeVar

from .type import Dynamic, Signature, make_default_value
from .signal import Signal
from .future import Future

T = TypeVar("T")


class Property(Generic[T]):
    def __init__(self, signature: str | Signature = Dynamic):
        self._signature = signature
        self._on_change = Signal[T](signature)
        self._value: T = make_default_value(signature)  # type: ignore
        self.addCallback = self.connect

    def value(self, _async: bool = False) -> T | Future[T]:
        """
        Return the value stored inside the property.
        """
        return Future(self._value) if _async else self._value

    def setValue(self, value: T, _async: bool = False) -> None | Future[None]:
        """
        Set the value of the property.
        """
        changed = value != self._value
        self._value = value
        if changed:
            self._on_change(value)
        return Future(None) if _async else None

    def connect(
        self, cb: Callable[[T], None], _async: bool = False
    ) -> int | Future[int]:
        """
        Add an event subscriber to the property.

        :param cb: the callback to call when the property changes.
        :returns: the id of the property subscriber,
        """
        return self._on_change.connect(cb, _async=_async)

    def disconnect(self, id: int, _async: bool = False) -> bool | Future[bool]:
        """
        Disconnect the callback associated to id.

        :param id: the connection id returned by :method:connect or :method:addCallback
        :returns: True on success.
        """
        return self._on_change.disconnect(id, _async=_async)

    def disconnectAll(self, _async: bool = False) -> bool | Future[bool]:
        """
        Disconnect all subscribers associated to the property.

        This function should be used with caution, as it may also remove
        subscribers that were added by other callers.

        :returns: True on success
        """
        return self._on_change.disconnectAll(_async=_async)
