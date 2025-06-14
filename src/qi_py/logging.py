__all__ = [
    "SILENT",
    "FATAL",
    "ERROR",
    "WARNING",
    "INFO",
    "VERBOSE",
    "DEBUG",
    "fatal",
    "error",
    "warning",
    "info",
    "verbose",
    "Logger",
    "setLevel",
    "setContext",
    "setFilters",
]

import logging
import os
import sys
from enum import Enum
from typing import Any
from termcolor import colored


class LogLevel(Enum):
    Silent = 0
    Fatal = 1
    Error = 2
    Warning = 4
    Info = 5
    Verbose = 6
    Debug = 7

    def to_python_logging_value(self, logger: bool) -> int:
        match self:
            case LogLevel.Silent:
                # For a logger, a silent level means that it does not log anything from DEBUG to
                # FATAL, i.e. its logging level is beyond FATAL.
                if logger:
                    return logging.FATAL + 1
                # For a log record, a silent level means that it's a lower level than DEBUG.
                else:
                    return logging.DEBUG - 1
            case LogLevel.Fatal:
                return logging.FATAL
            case LogLevel.Error:
                return logging.ERROR
            case LogLevel.Warning:
                return logging.WARNING
            case LogLevel.Info:
                return logging.INFO
            case LogLevel.Verbose:
                return VERBOSE_LEVEL_VALUE
            case LogLevel.Debug:
                return logging.DEBUG


VERBOSE_LEVEL_VALUE = int((logging.INFO + logging.DEBUG) / 2)

SILENT = LogLevel.Silent
FATAL = LogLevel.Fatal
ERROR = LogLevel.Error
WARNING = LogLevel.Warning
INFO = LogLevel.Info
VERBOSE = LogLevel.Verbose
DEBUG = LogLevel.Debug


class StdoutFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return "{level} {date} {tid} {message}".format(
            level=self.short_level_name(record.levelno),
            date=self.time(record.created),
            tid=record.thread,
            message=record.msg,
        )

    def formatStack(self, stack_info):
        return ""

    @staticmethod
    def short_level_name(level: int) -> str:
        match level:
            case logging.FATAL:
                return colored("[F]", "magenta")
            case logging.ERROR:
                return colored("[E]", "red")
            case logging.WARNING:
                return colored("[W]", "yellow")
            case logging.INFO:
                return colored("[I]", "blue")
            case value if value == VERBOSE_LEVEL_VALUE:
                return colored("[V]", "green")
            case logging.DEBUG:
                return colored("[D]", "white")
            case _:
                return "[?]"

    @staticmethod
    # created: Time when the LogRecord was created (as returned by time.time_ns() / 1e9).
    def time(created: float) -> str:
        return f"{created:.6f}"


LOGGER_NAME = "qi"


def init_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    handler: logging.Handler | None = None

    def make_journald_handler() -> logging.Handler | None:
        try:
            from systemd import journal  # type: ignore

            args = {}
            syslog_identifier = os.environ.get("QI_SYSLOG_IDENTIFIER")
            if syslog_identifier is not None:
                args["SYSLOG_IDENTIFIER"] = syslog_identifier
            return journal.JournalHandler(**args)
        except ModuleNotFoundError:
            return None

    def make_stdout_handler():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StdoutFormatter())
        return handler

    match os.environ.get("QI_DEFAULT_LOGHANDLER"):
        case None:
            handler = make_journald_handler()
            if handler is None:
                handler = make_stdout_handler()
        case "logger":
            handler = make_journald_handler()
        case "stdout":
            handler = make_stdout_handler()
    if handler is not None:
        logger.addHandler(handler)


init_logger()


def log(level: LogLevel, category: str, message: str | Any, *args):
    logger = logging.getLogger(LOGGER_NAME)
    full_message = " ".join(map(str, [message] + list(args)))
    logger.log(
        level.to_python_logging_value(False),
        f"{category}: {full_message}",
        stack_info=True,
        stacklevel=3,  # skip logging functions frames
        extra={"QI": 1, "QI_CATEGORY": category},
    )


class Logger:
    def __init__(self, category):
        self.category = category

    def fatal(self, message, *args):
        """
        Logs a message with level FATAL on this logger.

        :param message: Messages string
        :param *args: Messages format string working the same way as python
                      function print.
        """
        log(FATAL, self.category, message, *args)

    def error(self, message, *args):
        """
        Logs a message with level ERROR on this logger.

        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        """
        log(ERROR, self.category, message, *args)

    def warning(self, message, *args):
        """
        Logs a message with level WARNING on this logger.

        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        """
        log(WARNING, self.category, message, *args)

    def info(self, message, *args):
        """
        Logs a message with level INFO on this logger.

        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        """
        log(INFO, self.category, message, *args)

    def verbose(self, message, *args):
        """
        Logs a message with level VERBOSE on this logger.

        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        """
        log(VERBOSE, self.category, message, *args)


def fatal(category, message, *args):
    """
    Logs a message with level FATAL.

    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    """
    log(FATAL, category, message, *args)


def error(category, message, *args):
    """
    Logs a message with level ERROR.

    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    """
    log(ERROR, category, message, *args)


def warning(category, message, *args):
    """
    Logs a message with level WARNING.

    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    """
    log(WARNING, category, message, *args)


def info(category, message, *args):
    """
    Logs a message with level INFO.

    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    """
    log(INFO, category, message, *args)


def verbose(category, message, *args):
    """
    Logs a message with level VERBOSE.

    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    """
    log(VERBOSE, category, message, *args)


def setLevel(level: LogLevel):
    """
    Sets the threshold for the logger to level.
    Logging messages which are less severe than level will be ignored.
    Note that the logger is created with level INFO.

    :param level: The minimum log level.
    """
    logging.getLogger(LOGGER_NAME).setLevel(
        level.to_python_logging_value(True))


def setContext(context: int):
    """
    1  : Verbosity
    2  : ShortVerbosity
    4  : Date
    8  : ThreadId
    16 : Category
    32 : File
    64 : Function
    128: EndOfLine
    Some useful values for context are:
    26 : (verb+threadId+cat)
    30 : (verb+threadId+date+cat)
    126: (verb+threadId+date+cat+file+fun)
    254: (verb+threadId+date+cat+file+fun+eol)

    :param context: A bitfield (sum of described values).
    """
    # TODO
    warning("logging", "logging.setContext function is not implemented yet")


def setFilters(filters: str):
    """
    Set log filtering options.
    Each rule can be:
      +CAT: enable category CAT
      -CAT: disable category CAT
      CAT=level : set category CAT to level
    Each category can include a '*' for globbing.

    .. code-block:: python

      qi.logging.setFilter(\"qi.*=debug:-qi.foo:+qi.foo.bar\")

    (all qi.* logs in info, remove all qi.foo logs except qi.foo.bar)

    :param filters: List of rules separated by colon.
    """
    # TODO
    warning("logging", "logging.setFilters function is not implemented yet")
