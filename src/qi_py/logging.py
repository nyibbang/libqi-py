import logging
import os
import sys
from enum import Enum
from typing import Any

__all__ = [
    "SILENT", "FATAL", "ERROR", "WARNING", "INFO", "VERBOSE", "DEBUG",
    "fatal", "error", "warning", "info", "verbose",
    "Logger", "setLevel", "setContext", "setFilters"
]

LOGGER_NAME = "qi"

def init_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    handlers: list[logging.Handler] = []
    def make_stdout_handler():
        return logging.StreamHandler(sys.stdout)
    match os.environ.get("QI_DEFAULT_LOGHANDLER"):
        case (None | "logger") as default_handler_env:
            try:
                from systemd import journal
                args = {}
                syslog_identifier = os.environ.get("QI_SYSLOG_IDENTIFIER")
                if syslog_identifier is not None:
                    args["SYSLOG_IDENTIFIER"] = syslog_identifier
                handlers.append(journal.JournalHandler(**args))
            except ModuleNotFoundError:
                if default_handler_env is None:
                    # No systemd module, fallback to stdout if none was set as environnement variable.
                    handlers.append(make_stdout_handler())
        case "stdout":
            handlers.append(make_stdout_handler())
    for handler in handlers:
        logger.addHandler(handler)

init_logger()

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
                if logger:
                    return logging.CRITICAL + 1
                else:
                    return logging.DEBUG - 1
            case LogLevel.Fatal:
                return logging.CRITICAL
            case LogLevel.Error:
                return logging.ERROR
            case LogLevel.Warning:
                return logging.WARNING
            case LogLevel.Info:
                return logging.INFO
            case LogLevel.Verbose:
                return VERBOSE_LEVEL_PYTHON_LOGGING_VALUE
            case LogLevel.Debug:
                return logging.DEBUG

VERBOSE_LEVEL_PYTHON_LOGGING_VALUE = int((logging.INFO + logging.DEBUG) / 2)

SILENT = LogLevel.Silent
FATAL = LogLevel.Fatal
ERROR = LogLevel.Error
WARNING = LogLevel.Warning
INFO = LogLevel.Info
VERBOSE = LogLevel.Verbose
DEBUG = LogLevel.Debug

def log(level: LogLevel, category: str, message: str | Any, *args):
    logger = logging.getLogger(LOGGER_NAME)
    full_message = " ".join(map(str, [message] + list(args)))
    logger.log(
            level.to_python_logging_value(False),
            f"{category}: {full_message}",
            stack_info=True,
            stacklevel=3, # skip logging functions frames
            extra={"QI": 1, "QI_CATEGORY": category})

class Logger:
    def __init__(self, category):
        self.category = category

    def fatal(self, message, *args):
        """ fatal(message, *args) -> None
        :param message: Messages string
        :param *args: Messages format string working the same way as python
                      function print.
        Logs a message with level FATAL on this logger."""
        log(FATAL, self.category, message, *args)

    def error(self, message, *args):
        """ error(message, *args) -> None
        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        Logs a message with level ERROR on this logger."""
        log(ERROR, self.category, message, *args)

    def warning(self, message, *args):
        """ warning(message, *args) -> None
        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        Logs a message with level WARNING on this logger."""
        log(WARNING, self.category, message, *args)

    def info(self, message, *args):
        """ info(message, *args) -> None
        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        Logs a message with level INFO on this logger."""
        log(INFO, self.category, message, *args)

    def verbose(self, message, *args):
        """ verbose(message, *args) -> None
        :param message: Messages string
        :param *args: Arguments are interpreted as for
                      :py:func:`qi.Logger.fatal`.
        Logs a message with level VERBOSE on this logger."""
        log(VERBOSE, self.category, message, *args)

def fatal(category, message, *args):
    """ fatal(category, message, *args) -> None
    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    Logs a message with level FATAL."""
    log(FATAL, category, message, *args)

def error(category, message, *args):
    """ error(category, message, *args) -> None
    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    Logs a message with level ERROR."""
    log(ERROR, category, message, *args)

def warning(category, message, *args):
    """ warning(category, message, *args) -> None
    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    Logs a message with level WARNING."""
    log(WARNING, category, message, *args)

def info(category, message, *args):
    """ info(category, message, *args) -> None
    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    Logs a message with level INFO."""
    log(INFO, category, message, *args)

def verbose(category, message, *args):
    """ verbose(category, message, *args) -> None
    :param category: The category is potentially a period-separated hierarchical
                value.
    :param message: Messages string
    :param *args: Messages format string working the same way as print python
                  function.
    Logs a message with level VERBOSE."""
    log(VERBOSE, category, message, *args)

def setLevel(level: LogLevel):
    """
    Sets the threshold for the logger to level.
    Logging messages which are less severe than level will be ignored.
    Note that the logger is created with level INFO.

    :param level: The minimum log level.
    """
    logging.getLogger(LOGGER_NAME).setLevel(level.to_python_logging_value(True))

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
