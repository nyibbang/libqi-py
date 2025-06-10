from typing import Any
from ._object import Object as _Object


class Signature:
    def __init__(self, signature):
        self.signature = signature

    def __str__(self):
        return self.signature

    def __unicode__(self):
        return self.signature

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.signature
        return other.signature == self.signature

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self


Void = Signature("v")
"""Void Type"""

Bool = Signature("b")
"""Bool Type"""

Int8 = Signature("c")
"""Signed 8 bits Integer Type"""

UInt8 = Signature("C")
"""Unsigned 8 bits Integer Type"""

Int16 = Signature("w")
"""Signed 16 bits Integer Type"""

UInt16 = Signature("W")
"""Unsigned 16 bits Integer Type"""

Int32 = Signature("i")
"""Signed 32 bits Integer Type"""

UInt32 = Signature("I")
"""Unsigned 32 bits Integer Type"""

Int64 = Signature("l")
"""Signed 64 bits Integer Type"""

UInt64 = Signature("L")
"""Unsigned 64 bits Integer Type"""

Float = Signature("f")
"""32 bits Floating Point Type"""

Double = Signature("d")
"""64 bits Floating Point Type"""

String = Signature("s")
"""String Type"""


def List(value):
    """List Type, a value type need to be specified"""
    return Signature(f"[{value}]")


def Optional(value):
    """Optional Type, a value type need to be specified"""
    return Signature(f"+{value}")


def Map(key, value):
    """List Type, a key and an element type need to be specified"""
    return Signature(f"{{{key}{value}}}")


def Struct(fields):
    """Structure Type"""
    return Signature("(%s)" % fields.join(""))


Object = Signature("o")
"""Object Type"""

Dynamic = Signature("m")
"""Any Type"""

Buffer = Signature("r")
"""Buffer Type"""


# Yes this look similar to Dynamic but it's not.
# eg: qi_py.bind(Void, (Dynamic, Dynamic))  this mean a tuple of two dynamic.
# eg: qi_py.bind(Void, AnyArguments)        this is not a tuple. (m not in tuple,
#                                           mean anythings)
# eg: qi_py.bind(Void, Dynamic)             this is a function with one argument
AnyArguments = Signature("m")
"""
Any Arguments Types. A function or a signal taking AnyArguments
will accept all kind of arguments. AnyArguments is a list of AnyValue
"""


# Return the qi_py.type of the parameter
def typeof(a):
    """return the qi type of a variable
    .. warning::
       this function is only implemented for Object
    """
    if isinstance(a, _Object):
        return Object
    raise NotImplementedError("typeOf is only implemented for Object right now")


# Cant be called isinstance or typeof will run into infinite loop
# See qi_py.__init__ for the renaming
def _isinstance(a, type):
    """return true if `a` is of type `type`
    .. warning::
       this function is only implemented for Object
    """
    if type != Object:
        raise NotImplementedError("isinstance is only implemented for Objectright now")
    try:
        return typeof(a) == type
    except NotImplementedError:
        return False
