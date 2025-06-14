from pathlib import Path

__all__ = [
    "findBin",
    "findLib",
    "findConf",
    "findData",
    "listData",
    "confPaths",
    "dataPaths",
    "binPaths",
    "libPaths",
    "setWritablePath",
    "userWritableDataPath",
    "userWritableConfPath",
    "sdkPrefix",
    "sdkPrefixes",
    "addOptionalSdkPrefix",
    "clearOptionalSdkPrefix",
]


def sdkPrefix() -> Path:
    """The SDK prefix path. It is always a complete, native path."""
    # TODO
    raise NotImplementedError()


def findBin(name, searchInPath=False) -> Path:
    """
    Look for a binary in the system.

    :param name: string. The full name of the binary, or just the name.
    :param searchInPath: boolean. Search in $PATH if it hasn't been found in sdk dirs. Optional.

    :returns: the complete, native path to the file found. An empty string otherwise.
    """
    # TODO
    raise NotImplementedError()


def findLib(name) -> Path:
    """
    Look for a library in the system.

    :param name: string. The full name of the library, or just the name.

    :returns: the complete, native path to the file found. An empty string otherwise.
    """
    # TODO
    raise NotImplementedError()


def findConf(application, file, excludeUserWritablePath=False) -> Path:
    """
    Look for a configuration file in the system.

    :param application: string. The name of the application.
    :param file: string. The name of the file to look for. You can specify subdirectories using '/' as a separator.
    :param excludeUserWritablePath: If true, findConf() won't search into userWritableConfPath.

    :returns: the complete, native path to the file found. An empty string otherwise.
    """
    # TODO
    raise NotImplementedError()


def findData(application, file, excludeUserWritablePath=False) -> Path:
    """
    Look for a file in all dataPaths(application) directories. Return the first match.

    :param application: string. The name of the application.
    :param file: string. The name of the file to look for. You can specify subdirectories using a '/' as a separator.
    :param excludeUserWritablePath: If true, findData() won't search into userWritableDataPath.

    :returns: the complete, native path to the file found. An empty string otherwise.
    """
    # TODO
    raise NotImplementedError()


def listData(applicationName, pattern="*") -> list[Path]:
    """
    List data files matching the given pattern in all `dataPaths(application)` directories.

    For each match, return the occurrence from the first dataPaths prefix. Directories are discarded.

    :param application: string. The name of the application.
    :param patten: string. Wildcard pattern of the files to look for. You can specify subdirectories using a '/' as a separator. "*" by default.

    :returns: a list of the complete, native paths of the files that matched.
    """
    # TODO
    raise NotImplementedError()


def confPaths(applicationName="") -> list[Path]:
    """
    Get the list of directories used when searching for configuration files for the given application.

    :param applicationName: string. Name of the application. "" by default.

    :returns: The list of configuration directories.

    .. warning::
        You should not assume those directories exist, nor that they are writable.
    """
    # TODO
    raise NotImplementedError()


def dataPaths(applicationName="") -> list[Path]:
    """
    Get the list of directories used when searching for configuration files for the given application.

    :param application: string. Name of the application. "" by default.

    :returns: The list of data directories.

    .. warning::
        You should not assume those directories exist, nor that they are writable.
    """
    # TODO
    raise NotImplementedError()


def binPaths() -> list[Path]:
    """
    :returns: The list of directories used when searching for binaries.

    .. warning::
        You should not assume those directories exist, nor that they are writable.
    """
    # TODO
    raise NotImplementedError()


def libPaths() -> list[Path]:
    """
    :returns: The list of directories used when searching for libraries.

    .. warning::
        You should not assume those directories exist, nor that they are writable.
    """
    # TODO
    raise NotImplementedError()


def setWritablePath(path) -> None:
    """
    Set the writable files path for users.

    :param path: string. A path on the system. Use an empty path to reset it to its default value.
    """
    # TODO
    raise NotImplementedError()


def userWritableDataPath(applicationName, fileName) -> Path:
    """
    Get the writable data files path for users.

    :param applicationName: string. Name of the application.
    :param fileName: string. Name of the file.

    :returns: The file path.
    """
    # TODO
    raise NotImplementedError()


def userWritableConfPath(applicationName, fileName) -> Path:
    """
    Get the writable configuration files path for users.

    :param applicationName: string. Name of the application.
    :param fileName: string. Name of the file.

    :returns: The file path.
    """
    # TODO
    raise NotImplementedError()


def sdkPrefixes() -> list[Path]:
    """
    List of SDK prefixes.

    :returns: The list of sdk prefixes.
    """
    # TODO
    raise NotImplementedError()


def addOptionalSdkPrefix(prefix) -> None:
    """
    Add a new SDK path prefix.
    """
    # TODO
    raise NotImplementedError()


def clearOptionalSdkPrefix() -> None:
    """Clear all optional sdk prefixes."""
    # TODO
    raise NotImplementedError()
