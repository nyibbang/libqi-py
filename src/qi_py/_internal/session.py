from dataclasses import dataclass
from typing import Tuple
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

    def connect(
        self,
        url: str = default_connect_url,
        _overload: str | None = None,
        _async: bool = False,
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
        self, _overload: str | None = None, _async: bool = False
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def isConnected(
        self, _overload: str | None = None, _async: bool = False
    ) -> bool | Future[bool]:
        # TODO
        raise NotImplementedError()

    def endpoints(
        self, _overload: str | None = None, _async: bool = False
    ) -> list[str] | Future[list[str]]:
        # TODO
        raise NotImplementedError()

    def url(
        self, _overload: str | None = None, _async: bool = False
    ) -> str | Future[str]:
        # TODO
        raise NotImplementedError()

    def services(
        self, _overload: str | None = None, _async: bool = False
    ) -> list[ServiceInfo] | Future[list[ServiceInfo]]:
        # TODO
        raise NotImplementedError()

    def waitForService(
        self,
        name: str,
        timeout: int | float = default_wait_for_service_timeout,
        _overload: str | None = None,
        _async: bool = False,
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def service(
        self,
        name: str,
        timeout: int | float = default_service_timeout,
        _overload: str | None = None,
        _async: bool = False,
    ) -> Object | Future[Object]:
        # TODO
        raise NotImplementedError()

    def registerService(
        self,
        name: str,
        service: str,
        _overload: str | None = None,
        _async: bool = False,
    ) -> int | Future[int]:
        # TODO
        raise NotImplementedError()

    def unregisterService(
        self, id: int, _overload: str | None = None, _async: bool = False
    ) -> None | Future[None]:
        # TODO
        raise NotImplementedError()

    def loadServiceRename(
        self,
        module: str,
        rename: str,
        *args,
        _overload: str | None = None,
        _async: bool = False,
    ):
        raise NotImplementedError("modules are not supported in qi_py")

    def callModule(
        self,
        module: str,
        *args,
        _overload: str | None = None,
        _async: bool = False,
    ):
        raise NotImplementedError("modules are not supported in qi_py")
