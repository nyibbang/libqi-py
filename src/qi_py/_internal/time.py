import time


def clockNow():
    """
    The current time in a system-wide clock, best suitable for timestamping events.
    Typically monotonic and unaffected by the system clock adjustment, altough this is not guaranteed.

    :returns: current timestamp since epoch as a number of nanoseconds.
    """
    return steadyClockNow()


def steadyClockNow():
    """
    The current time in a monotonic clock.

    The time points of this clock cannot decrease as physical time moves forward. This clock is not
    related to wall clock time, and is best suitable for measuring intervals.

    :returns: current timestamp since epoch as a number of nanoseconds.
    """
    return time.monotonic_ns()


def systemClockNow():
    """
    A system-wide real time wall clock. It may not be monotonic: on most systems, the system time can
    be adjusted at any moment.

    :returns: current timestamp since epoch as a number of nanoseconds.
    """
    return time.time_ns()
