from dataclasses import dataclass
from enum import IntEnum
from functools import partial
import inspect
import time
from typing import Callable, Any, Generic, TypeVar
import weakref
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
    on_cancel: Callable[[], Any] | None
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


T = TypeVar("T")
U = TypeVar("U")


class Promise(Generic[T]):
    def __init__(self, on_cancel=None):
        """
        :param on_cancel: a function that will be called when a cancel is requested on the future.
        """

        self._internal = Internal(
            event_loop().create_future(),
            lambda: invoke_on_cancel(on_cancel, self),
        )

    def setOnCancel(
        self, on_cancel: Callable[["Promise[T]"], Any] | None = None
    ) -> None:
        self._internal.on_cancel = lambda: invoke_on_cancel(on_cancel, self)

    def setCanceled(self):
        """Set the state of the promise to Canceled."""
        # If the Future is already done or cancelled, Future.cancel() returns False. Otherwise, the state of
        # the future is immediately set to cancelled.
        if not self._internal.future.cancel():
            raise RuntimeError("Future has already been set.")

    def setError(self, error: Exception | str) -> None:
        """Set the error of the promise."""
        if isinstance(error, Exception):
            exception = error
        else:
            exception = Exception(error)
        self._internal.future.set_exception(exception)

    def setValue(self, value: T) -> None:
        """Set the value of the promise."""
        self._internal.future.set_result(value)

    def future(self) -> "Future[T]":
        """Get a future tied to the promise. You can get multiple futures from the same promise."""
        return Future(self._internal)

    def isCancelRequested(self) -> bool:
        """:returns: True if the future associated with the promise asked for cancellation."""
        return self._internal.cancel_requested


def PromiseNoop(*_):
    """No operation function
    .. deprecated:: 1.5.0"""
    pass


class Future(Generic[T]):
    def __init__(self, value: T | Internal | asyncio.Future):
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

    def get_loop(self) -> asyncio.AbstractEventLoop:
        return self._internal.future.get_loop()

    async def wait_for(self, timeout: int | float) -> None:
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

    def value(self, timeout: int | float = FutureTimeout.Infinite) -> T:
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

    def addCallback(self, callback: Callable[["Future[T]"], Any]) -> None:
        """
        Add a callback that will be called when the future becomes ready.

        The callback will be called even if the future is already ready.
        The first argument of the callback is the future itself.

        :param callback: a callable, could be a method or a function.
        """
        self._internal.future.add_done_callback(lambda _: callback(self))

    def then(self, callback: Callable[["Future[T]"], U]) -> "Future[U]":
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

    def andThen(self, callback: Callable[[T], U]) -> "Future[U]":
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


def futureBarrier(
    futureList, loop: asyncio.AbstractEventLoop | None = None
) -> Future[list[Future]]:
    """
    Return a future that will be set with all the futures given as argument when they are all finished.
    This is useful to wait for a bunch of Futures at once.

    :param futureList: A list of Futures to wait for.
    :param loop: An event loop to use for scheduling. If set to `None`, it will use the module global event loop.
    :returns: A Future of list of futureList.
    """

    async def wait_all():
        (done, pending) = await asyncio.wait(futureList)
        assert len(pending) == 0
        return list(done)

    loop = loop or event_loop()
    return Future(loop.create_task(wait_all()))


def runAsync(
    callback: Callable[..., T],
    *args,
    delay: int | float = 0,
    loop: asyncio.AbstractEventLoop | None = None,
) -> Future[T]:
    """
    :param callback: the callback that will be called
    :param delay: an optional delay in microseconds
    :param loop: An event loop to use for scheduling. If set to `None`, it will use the module global event loop.
    :returns: a future with the return value of the function
    """
    delay = float(delay) / 1e3  # get delay in seconds

    async def sleep_then_invoke_callback():
        await asyncio.sleep(delay)
        return callback(*args)

    loop = loop or event_loop()
    return Future(loop.create_task(sleep_then_invoke_callback()))


class PeriodicTask:
    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        """
        :param loop: An event loop to use for scheduling. If set to `None`, it will use the module global event loop.
        """
        self._callback: Callable | None = None
        self._period: float | None = None  # in seconds
        self._name = f"PeriodicTask_{id(self)}"
        self._compensate = False
        self._loop = loop or event_loop()
        self._task: asyncio.Task | None = None

    @staticmethod
    async def invoke_callback(
        callback, period: float, compensate: bool, immediate: bool
    ):
        if not immediate:
            await asyncio.sleep(period)
        while True:
            if compensate:
                before_call = time.monotonic()
            if inspect.isawaitable(callback):
                await callback
            else:
                # `callback` is possibly blocking, so we run it in some dedicated separate thread.
                await asyncio.to_thread(callback)
            delay = period
            if compensate:
                after_call = time.monotonic()
                delay -= after_call - before_call  # type: ignore
            await asyncio.sleep(delay)

    def setCallback(self, callable: Callable) -> None:
        """
        Set the callback used by the periodic task, this function can only be called once.

        :param callable: a python callable, could be a method or a function.
        :raises: a RuntimeError if a callbacck has already been set.
        """
        if self._callback is not None:
            raise RuntimeError("Callback has already been set")
        self._callback = callable

    def setUsPeriod(self, usPeriod: int | float) -> None:
        """
        Set the call interval in microseconds.
        This call will wait until next callback invocation to apply the change.
        To apply the change immediately, use:

        .. code-block:: python
            task.stop()
            task.setUsPeriod(
                100
            )
            task.start()

        :param usPeriod: the period in microseconds
        :raises: a ValueError if the period is negative.
        """
        period = float(usPeriod) / 1e3
        if period < 0:
            raise ValueError("Period cannot be negative")
        self._period = period

    def start(self, immediate) -> None:
        """
        Start the periodic task at specified period. No effect if already running.

        :param immediate: if true, first schedule of the task will happen with no delay.
        """
        if self._task is not None:
            return
        if self._callback is None:
            raise RuntimeError(
                "Periodic task cannot start without a setCallback() call first"
            )
        if self._period is None or self._period < 0:
            raise RuntimeError(
                "Periodic task cannot start without a setPeriod() call first"
            )
        self._task = self._loop.create_task(
            PeriodicTask.invoke_callback(
                self._callback, self._period, self._compensate, immediate
            )
        )

        def reset_self_task(weak, _):
            ref = weak()
            if ref is None:
                return
            ref.task = None

        self._task.add_done_callback(
            partial(reset_self_task, weakref.ref(self))
        )

    def stop(self) -> None:
        """
        Stop the periodic task. When this function returns, the callback will not be called anymore.
        Can be called from within the callback function.
        """
        if self._task is None:
            return
        self._task.cancel()

    def asyncStop(self):
        """
        Request for periodic task to stop asynchronously.
        Can be called from within the callback function.
        """
        self.stop()

    def compensateCallbackTime(self, compensate: bool):
        """
        :param compensate: boolean. True to activate the compensation. When compensation is activated, call interval
        will take into account call duration to maintain the period.

        .. warning::
            when the callback is longer than the specified period, compensation will result in the callback being
            called successively without pause.
        """
        self._compensate = compensate

    def setName(self, name: str) -> None:
        """Set name for debugging and tracking purpose"""
        self._name = name
        if self._task is not None:
            self._task.set_name(name)

    def isRunning(self) -> bool:
        """:returns: true if task is running"""
        return self._task is not None and not self._task.cancelled()

    def isStopping(self) -> bool:
        """
        Can be called from within the callback to know if stop() or asyncStop() was called.

        returns: whether state is stopping or stopped.
        """
        return not self.isRunning()
