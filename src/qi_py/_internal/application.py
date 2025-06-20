import asyncio
import sys

_event_loop_instance = None


def event_loop() -> asyncio.AbstractEventLoop:
    global _event_loop_instance
    if _event_loop_instance is None:
        _event_loop_instance = asyncio.new_event_loop()
    return _event_loop_instance


_instance = None


def Application(args=None, raw=False, autoExit=True, url=None):
    """Instantiates and returns the Application instance."""
    global _instance
    if _instance is None:
        if args is None:
            args = sys.argv
        if url is None:
            url = ""
        if not args:
            args = [sys.executable]
        elif args[0] == "":
            args[0] = sys.executable
        if raw:
            _instance = ApplicationSimple(args)
        else:
            _instance = ApplicationSession(args, autoExit, url)
    else:
        raise Exception("Application was already initialized")
    return _instance


class ApplicationSimple:
    def __init__(self, args):
        # TODO
        raise NotImplementedError()

    def run(self) -> None:
        """
        Block and execute the application event loop until the application is
        stopped or an interruption or termination signal is received.
        """
        # TODO
        raise NotImplementedError()

    @staticmethod
    def stop() -> None:
        """
        Stop the application.
        """
        # TODO
        raise NotImplementedError()


class ApplicationSession(ApplicationSimple):
    def __init__(self, args, autoExit, url):
        self._url = url
        self._session = None

    def run(self):
        # TODO
        raise NotImplementedError()

    def start(self) -> None:
        """
        Start the connection of the session, once this function is called everything is fully
        initialized and working.
        """
        # TODO
        raise NotImplementedError()

    @staticmethod
    def atRun(func):
        """
        Add a callback that will be executed when run() is called.
        """
        # TODO
        raise NotImplementedError()

    @property
    def url(self):
        """
        The session associated to the application.
        """
        return self._url

    @property
    def session(self):
        """
        The url given to the Application. It's the url used to connect the session.
        """
        return self._session


def instance() -> ApplicationSimple | ApplicationSession:
    if _instance is None:
        raise Exception("Application not initialized")
    return _instance
