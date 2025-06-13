import inspect
from ._type import AnyArguments, Dynamic, Tuple
from enum import Enum
from dataclasses import dataclass


class Threading(Enum):
    Single = 1
    Multi = 2


@dataclass
class Binding:
    name: str
    parameters_signature: str
    return_signature: str


# Gets the default signature for a method.
#
# If the function takes variadic arguments (vargs), returns the signature of a
# pure dynamic element, which indicates a generic function that takes anything.
#
# Otherwise, returns the signature of a function taking n Python objects, with n
# the number of positional parameters the function accepts.
def method_default_parameters_signature(fn) -> str:
    parameters = inspect.signature(fn).parameters

    # If there any vargs parameter, then the parameters signature is dynamic.
    if any(
        parameter.kind == inspect.Parameter.VAR_POSITIONAL
        for parameter in parameters.values()
    ):
        return str(Dynamic)

    # Count the number of positional arguments
    def is_positional(parameter):
        return (
            parameter.kind == inspect.Parameter.POSITIONAL_ONLY
            or parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        )

    positional_count = sum(
        is_positional(parameter) for parameter in parameters.values()
    )

    return str(Tuple([Dynamic] * positional_count))


class bind:
    """Allows specifying types and methodName for bound methods."""

    def __init__(self, returnType=None, paramsType=None, methodName=None) -> None:
        self.return_signature = str(returnType or Dynamic)
        if paramsType is None:
            self.parameters_signature = None
        elif isinstance(paramsType, (list, tuple)):
            self.parameters_signature = str(Tuple(paramsType))
        elif isinstance(paramsType, AnyArguments) or (
            inspect.isclass(paramsType) and issubclass(paramsType, AnyArguments)
        ):
            self.parameters_signature = str(Dynamic)
        else:
            raise Exception("Invalid types for parameters")
        self.name = methodName

    def __call__(self, fn):
        name = self.name
        if name is None:
            name = fn.__name__

        parameters_signature = self.parameters_signature
        if parameters_signature is None:
            parameters_signature = method_default_parameters_signature(fn)

        fn._qi_binding = Binding(name, parameters_signature, self.return_signature)
        return fn


def nobind(fn):
    """This function decorator will prevent the function from being bound."""
    fn._qi_binding = None
    return fn


def singleThreaded(self, fn):
    """
    This class decorator specifies that some methods of this class will
    never be called at the same time on the same instance by the qi_py library,
    by doing the calls sequentially and ensuring thread safety without the
    need of some extra synchronization mechanism.

    This guarantee only applies to method calls that originate from the qi_py
    module, which mostly concerns bound methods and methods connected as
    callbacks of signals.

    It does not apply to private methods (methods that start with
    '__'), including but not restricted to __init__, __del__, __enter__ and
    __exit__.

    One consequence of this is that a sequenced method call on an object
    must finish before another sequenced method call on the same object can
    be made.

    This is the default behavior.
    """

    def __init__(self, _):
        pass

    def __call__(self, f):
        """Function Generator"""
        f._qi_threading = Threading.Single
        return f


class multiThreaded(object):
    """
    This class decorator specifies that methods in the class are allowed to
    be called concurrently. This implies that the developer of the class
    must guarantee no concurrent access to it's internal data, usually by
    using some synchronization mechanism.
    """

    def __init__(self, _):
        pass

    def __call__(self, f):
        """Function Generator."""
        f._qi_threading = Threading.Multi
        return f
