from typing import Any, Callable, Dict, Type, Union, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

def identity(arg: C) -> C: ...

class compose:
    # I'm putting just the case of simple composition, and the chaining of several
    # homogeneous functions.  I'm disregarding the full_args and pos_args, because
    # Callable cannot express that.
    @overload
    def __call__(f: Callable[[A], B], g: Callable[[C], A]) -> Callable[[C], B]: ...
    @overload
    def __call__(*fn: Callable[[A], A]) -> Callable[[A], A]: ...
