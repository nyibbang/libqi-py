from dataclasses import dataclass
from enum import IntEnum
import inspect
from typing import Callable, Any
from ..logging import warning, error
from .application import event_loop
import asyncio


class FutureState(IntEnum):
    Invalid = 0
    Running = 1
    Canceled = 2
    FinishedWithError = 3
    FinishedWithValue = 4


class FutureTimeout(IntEnum):
    Zero = 0
    Infinite = 2**31 - 1


@dataclass
class Internal:
    future: asyncio.Future
    on_cancel: Callable[[]] | None
    cancel_requested: bool = False


class CanceledError(RuntimeError):
    def __init__(self):
        super().__init__("Future canceled.")


def raise_canceled_error():
    raise CanceledError()


class TimeoutError(RuntimeError):
    def __init__(self):
        super().__init__("Future timeout.")


def raise_timeout_error():
    raise TimeoutError()


class DoneError(RuntimeError):
    def __init__(self):
        super().__init__("Future has no error.")


def raise_done_error():
    raise DoneError()


def invoke_on_cancel(on_cancel, promise) -> None:
    if on_cancel is None:
        return
    try:
        on_cancel(promise)
    except Exception as ex:
        warning(
            "qi_py.future",
            f"Promise `on_cancel` callback raised an exception: {ex}",
        )


class Promise:
    def __init__(self, on_cancel=None):
        """
        :param on_cancel: a function that will be called when a cancel is requested on the future.
        """

        self._internal = Internal(
            event_loop().create_future(),
            lambda: invoke_on_cancel(on_cancel, self),
        )

    def setOnCancel(self, on_cancel=None) -> None:
        self._internal.on_cancel = lambda: invoke_on_cancel(on_cancel, self)

    def setCanceled(self):
        """Set the state of the promise to Canceled."""
        # If the Future is already done or cancelled, Future.cancel() returns False. Otherwise, the state of
        # the future is immediately set to cancelled.
        if not self._internal.future.cancel():
            raise RuntimeError("Future has already been set.")

    def setError(self, error) -> None:
        """Set the error of the promise."""
        if isinstance(error, Exception):
            exception = error
        else:
            exception = Exception(error)
        self._internal.future.set_exception(exception)

    def setValue(self, value) -> None:
        """Set the value of the promise."""
        self._internal.future.set_result(value)

    def future(self):
        """Get a future tied to the promise. You can get multiple futures from the same promise."""
        return Future(self._internal)

    def isCancelRequested(self) -> bool:
        """:returns: True if the future associated with the promise asked for cancellation."""
        return self._internal.cancel_requested


class Future:
    def __init__(self, value):
        """Create a future with a value."""
        if isinstance(value, Internal):
            self._internal = value
            return

        future = None
        if asyncio.isfuture(value):
            future = value
        else:
            future = event_loop().create_future()
            future.set_result(value)
        self._internal = Internal(future, lambda: future.cancel())

    def get_loop(self):
        return self._internal.future.get_loop()

    async def wait_for(self, timeout: int | float):
        """
        Run the future until completion or until some time has passed.

        :param timeout: a time in milliseconds. Optional.
        """
        # Shield the future to prevent `wait_for` to cancel it in case of timeout.
        shield_future = asyncio.shield(self._internal.future)

        # `wait_for` expects a timeout in seconds, while this method takes a timeout in
        # milliseconds.
        timeout_secs = float(timeout) / 1e3
        await asyncio.wait_for(shield_future, timeout_secs)

    def _block_invoke(
        self, timeout, on_value, on_error, on_canceled, on_timeout
    ):
        try:
            result = self.get_loop().run_until_complete(self.wait_for(timeout))
            return on_value(result)
        except asyncio.CancelledError:
            return on_canceled()
        except asyncio.exceptions.TimeoutError:
            return on_timeout()
        except Exception as err:
            return on_error(err)

    def value(self, timeout: int | float = FutureTimeout.Infinite):
        """
        Block until the future is ready.

        :param timeout: a time in milliseconds. Optional.
        :returns: the value of the future.
        :raises: a RuntimeError if the timeout is reached or the future has error.
        """

        def on_error(err):
            if isinstance(err, RuntimeError):
                raise err
            else:
                raise RuntimeError(err)

        return self._block_invoke(
            timeout,
            on_value=lambda value: value,
            on_error=on_error,
            on_canceled=raise_canceled_error,
            on_timeout=raise_timeout_error,
        )

    def error(self, timeout: int | float = FutureTimeout.Infinite) -> str:
        """
        Block until the future is finished with an error.

        :param timeout: a time in milliseconds. Optional.
        :returns: the error of the future.
        :raises: a RuntimeError if the timeout is reached or the future has no error.
        """
        return self._block_invoke(
            timeout,
            on_value=raise_done_error,
            on_error=lambda err: str(err),
            on_canceled=raise_canceled_error,
            on_timeout=raise_timeout_error,
        )

    def wait(
        self, timeout: int | float = FutureTimeout.Infinite
    ) -> FutureState:
        """
        Wait for the future to be ready.

        :param timeout: a time in milliseconds. Optional.
        :returns: a :data:`qi_py.FutureState`.
        """
        return self._block_invoke(
            timeout,
            on_value=lambda _: FutureState.FinishedWithValue,
            on_error=lambda _: FutureState.FinishedWithError,
            on_canceled=lambda _: FutureState.Canceled,
            on_timeout=lambda _: FutureState.Running,
        )

    def hasError(self, timeout: int | float = FutureTimeout.Infinite) -> bool:
        """
        :param timeout: a time in milliseconds. Optional.
        :returns: true iff the future has an error.
        :raise: a RuntimeError if the timeout is reached.
        """
        return self._block_invoke(
            timeout,
            on_value=lambda _: False,
            on_error=lambda _: True,
            on_canceled=lambda _: False,
            on_timeout=lambda _: raise_timeout_error,
        )

    def hasValue(self, timeout: int | float = FutureTimeout.Infinite) -> bool:
        """
        :param timeout: a time in milliseconds. Optional.
        :returns: true iff the future has a value.
        :raise: a RuntimeError if the timeout is reached.
        """
        return self._block_invoke(
            timeout,
            on_value=lambda _: True,
            on_error=lambda _: False,
            on_canceled=lambda _: False,
            on_timeout=lambda _: raise_timeout_error,
        )

    def cancel(self) -> None:
        """Ask for cancellation."""
        if self._internal.future.done() or self._internal.cancel_requested:
            return
        self._internal.cancel_requested = True
        if self._internal.on_cancel is not None:
            try:
                self._internal.on_cancel()
            except Exception as err:
                error(
                    "qi_py.future",
                    f"Future/Promise cancel handler threw an exception: {err}",
                )
            self._internal.on_cancel = None

    def isFinished(self) -> bool:
        """Return true if the future is not running anymore (i.e. if `hasError` or `hasValue` or
        `isCanceled`)."""
        return self._internal.future.done()

    def isRunning(self) -> bool:
        """Return true if the future is still running."""
        return not self.isFinished()

    def isCanceled(self) -> bool:
        """Return true if the future is canceled."""
        return not self._internal.future.cancelled()

    def isCancelable(self) -> bool:
        """
        :returns: always true, all future are cancellable now

        .. deprecated
        """
        return True

    def addCallback(self, callback: Callable[["Future"], None]) -> None:
        """
        Add a callback that will be called when the future becomes ready.

        The callback will be called even if the future is already ready.
        The first argument of the callback is the future itself.

        :param callback: a callable, could be a method or a function.
        """
        self._internal.future.add_done_callback(lambda _: callback(self))

    def then(self, callback: Callable[["Future"], Any]) -> "Future":
        """
        Add a callback that will be called when the future becomes ready.

        The callback will be called even if the future is already ready.
        The first argument of the callback is the future itself.

        :param callback: a callable, could be a method or a function.
        :returns: a future that will contain the return value of the callback.
        """
        future = self.get_loop().create_future()

        def then_invoke_callback(_) -> None:
            try:
                result = callback(self)
                future.set_result(result)
            except Exception as err:
                future.set_exception(err)

        self._internal.future.add_done_callback(then_invoke_callback)
        return Future(future)

    def andThen(self, callback: Callable) -> "Future":
        """
        Add a callback that will be called when the future becomes ready if it has a value.

        If the future finishes with an error, the callback is not called and the future returned by andThen is set to that error.

        The callback will be called even if the future is already ready.
        The first argument of the callback is the value of the future itself.

        :param callback: a callable, could be a method or a function.
        :returns: a future that will contain the return value of the callback.
        """

        async def and_then_invoke_callback():
            return callback(await self)

        return Future(self.get_loop().create_task(and_then_invoke_callback()))

    def unwrap(self) -> "Future":
        """
        If this is a Future of a Future of X, return a Future of X.

        The state of both futures is forwarded and cancel requests are forwarded to the appropriate future.
        """

        async def invoke_unwrap():
            result = await self
            if not inspect.isawaitable(result):
                error = "Unwrapping something that is not a nested future"
                warning("qi_py.future", error)
                raise RuntimeError(error)
            return await result

        return Future(self.get_loop().create_task(invoke_unwrap()))

    def __await__(self):
        return self._internal.future.__await__()


def futureBarrier(futureList):
    """
    Return a future that will be set with all the futures given as argument when they are all finished. This is useful to wait for a bunch of Futures at once.

    :param futureList: A list of Futures to wait for.
    :returns: A Future of list of futureList.
    """

    async def wait_all():
        (done, pending) = await asyncio.wait(futureList)
        assert len(pending) == 0
        return done

    return Future(event_loop().create_task(wait_all()))
