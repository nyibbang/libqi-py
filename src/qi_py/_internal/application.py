import asyncio
import sys


class Application:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise Exception("Application was already initialized")
        cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, args=None, raw=False, autoExit=True, url=None):
        if args is None:
            args = sys.argv
        if url is None:
            url = ""
        if not args:
            args = [sys.executable]
        elif args[0] == "":
            args[0] = sys.executable

        # if raw:
        #     _app = _Application(args)
        # else:
        #     _app = _ApplicationSession(args, autoExit, url)

    @classmethod
    def instance(cls) -> "Application":
        if cls._instance is None:
            raise Exception("Application not initialized")
        return cls._instance


ApplicationSession = Application

_event_loop_instance = None


def event_loop() -> asyncio.AbstractEventLoop:
    global _event_loop_instance
    if _event_loop_instance is None:
        _event_loop_instance = asyncio.new_event_loop()
    return _event_loop_instance
