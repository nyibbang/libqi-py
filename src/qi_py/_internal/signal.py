from typing import Callable, Generic, TypeVar

from ..logging import warning
from .future import Future
from .type import Signature, Dynamic

T = TypeVar("T")


class Signal(Generic[T]):
    def __init__(
        self,
        signature: str | Signature = Dynamic,
        onConnect: Callable[[bool], None] | None = None,
    ):
        self._signature = (
            signature
            if isinstance(signature, Signature)
            else Signature(signature)
        )
        self._on_connect = onConnect
        self._subscribers = {}
        self._next_id = 1

    def connect(
        self, callback: Callable[[T], None], _async=False
    ) -> int | Future[int]:
        """
        Connect the signal to a callback, the callback will be called each time the signal is
        triggered. Use the id returned to unregister the callback.

        :param callback: the callback that will be called when the signal is triggered.
        :returns: the connection id of the registered callback.
        """
        subscriber_id = self._next_id
        self._subscribers[subscriber_id] = callback
        self._next_id += 1
        # Invoke the `onConnect` callback if we had an empty subscribers list.
        if self._on_connect and len(self._subscribers) == 1:
            self._on_connect(True)
        return Future(subscriber_id) if _async else subscriber_id

    def disconnect(self, id: int, _async=False) -> bool | Future[bool]:
        """
        Disconnect the callback associated to id.

        :param id: the connection id returned by connect.
        :returns: true on success.
        """
        disconnected = self._subscribers.pop(id, None) is not None
        # Invoke `onConnect` if it was the last subscriber that was removed.
        if self._on_connect and not self._subscribers:
            self._on_connect(False)
        return Future(disconnected) if _async else disconnected

    def disconnectAll(self, _async=False) -> bool | Future[bool]:
        """
        Disconnect all subscribers associated to the property.

        This function should be used with caution, as it may also remove
        subscribers that were added by other callers.

        :returns: true on success
        """
        had_subscribers = bool(self._subscribers)
        self._subscribers.clear()
        if self._on_connect and had_subscribers:
            self._on_connect(False)
        return Future(True) if _async else True

    def __call__(self, *args: T) -> None:
        """Trigger the signal"""
        for callback in self._subscribers.values():
            try:
                callback(*args)
            except Exception as ex:
                warning(
                    "qi_py.signal",
                    f"Exception caught from signal sucbriber: {ex}",
                )
