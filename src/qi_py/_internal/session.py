from dataclasses import dataclass
from typing import Tuple, overload
from typing_extensions import Literal
from .object import Object
from .future import Future
from .signal import Signal


@dataclass
class ServiceInfo:
    name: str
    serviceId: int
    machineId: str
    processId: int
    endpoints: list[str]
    sessionId: str
    objectUid: str


default_service_timeout = 60 * 1000  # 1 minute as millisconds
default_wait_for_service_timeout = 5 * 60 * 1000  # 5 minutes as milliseconds
default_connect_url = "tcp://127.0.0.1:9559"
default_listen_url = "tcp://127.0.0.1:0"


class Session:
    def __init__(self):
        self.serviceRegistered = Signal[Tuple[int, str]]()
        self.serviceUnregistered = Signal[Tuple[int, str]]()
        self.connected = Signal[None]()
        self.disconnected = Signal[str]()
        self.sd_connection = None

    @overload
    def connect(
        self,
        url: str = ...,
        *,
        _async: Literal[False] = ...,
        _overload: str | None = ...,
    ) -> None: ...

    @overload
    def connect(
        self,
        url: str = ...,
        *,
        _async: Literal[True],
        _overload: str | None = ...,
    ) -> Future[None]: ...

    def connect(
        self,
        url: str = default_connect_url,
        *,
        _async: bool = False,
        _overload: str | None = None,
    ) -> None | Future[None]:
        future = Future(self.async_connect(url))
        return future if _async else future.value()

    async def async_connect(self, url: str | None = None) -> None:
        return

    def listen(
        self,
        url: str | list[str] = default_listen_url,
        _overload: str | None = None,
        _async: bool = False,
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def listenStandalone(
        self,
        url: str | list[str] | None = default_listen_url,
        _overload: str | None = None,
        _async: bool = False,
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def close(
        self, *, _async: bool = False, _overload: str | None = None
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def isConnected(
        self, *, _async: bool = False, _overload: str | None = None
    ) -> bool | Future[bool]:
        # TODO
        raise NotImplementedError()

    def endpoints(
        self, *, _async: bool = False, _overload: str | None = None
    ) -> list[str] | Future[list[str]]:
        # TODO
        raise NotImplementedError()

    def url(
        self, *, _async: bool = False, _overload: str | None = None
    ) -> str | Future[str]:
        # TODO
        raise NotImplementedError()

    def services(
        self, *, _async: bool = False, _overload: str | None = None
    ) -> list[ServiceInfo] | Future[list[ServiceInfo]]:
        # TODO
        raise NotImplementedError()

    def waitForService(
        self,
        name: str,
        timeout: int | float = default_wait_for_service_timeout,
        *,
        _async: bool = False,
        _overload: str | None = None,
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def service(
        self,
        name: str,
        timeout: int | float = default_service_timeout,
        *,
        _async: bool = False,
        _overload: str | None = None,
    ) -> Object | Future[Object]:
        # TODO
        raise NotImplementedError()

    def registerService(
        self,
        name: str,
        service: str,
        *,
        _async: bool = False,
        _overload: str | None = None,
    ) -> int | Future[int]:
        # TODO
        raise NotImplementedError()

    def unregisterService(
        self, id: int, *, _async: bool = False, _overload: str | None = None
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def loadServiceRename(
        self,
        module: str,
        rename: str,
        *args,
        _async: bool = False,
        _overload: str | None = None,
    ):
        raise NotImplementedError("modules are not supported in qi_py")

    def callModule(
        self,
        module: str,
        *args,
        _async: bool = False,
        _overload: str | None = None,
    ):
        raise NotImplementedError("modules are not supported in qi_py")
