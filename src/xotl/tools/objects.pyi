# flake8: noqa

from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import Protocol
from xotl.tools.symbols import Unset

# def adapt_exception(value: Optional[Union[Tuple[Type[KeyError], str], str, int]], **kwargs) -> Optional[KeyError]: ...
Getter = Callable[[Any], Callable[[str, Any], Any]]
Setter = Callable[[Any], Callable[[str, Any], None]]

def dict_merge(*dicts: Dict, **others) -> Dict: ...
def extract_attrs(obj: Any, *names: str, default: Any = ...) -> Tuple[Any, ...]: ...
def fulldir(obj: Dict[Any, Any]) -> Set[str]: ...
def get_first_of(
    source: Any, *keys: str, default: Any = ..., pred: Callable[[Any], bool] = ...
) -> Optional[Any]: ...
def get_traverser(
    *paths: str, default: Any = ..., sep: str = ..., getter: Getter = ...
) -> Callable: ...
def traverse(
    obj: Any,
    path: str,
    default: Any = Unset,
    sep: str = ".",
    getter: Optional[Getter] = None,
) -> Any: ...
def import_object(
    name: Union[object, str],
    package: str = ...,
    sep: str = ...,
    default: Any = ...,
    **kwargs,
) -> Any: ...
def iterate_over(source: Any, *keys) -> Iterator[Any]: ...
def pop_first_of(source: Any, *keys: str, default: Any = ...) -> Any: ...
def popattr(obj: Any, name: str, default: Any = None) -> Any: ...
def save_attributes(
    obj: Any, *attrs: str, getter: Getter = ..., setter: Setter = ...
) -> ContextManager: ...
def smart_copy(*args, defaults=...) -> Dict[str, Any]: ...
def smart_getter(obj: Any, strict: bool = ...) -> Callable[[str, Any], Any]: ...
def smart_getter_and_deleter(obj: Any) -> Callable[[str, Any], Any]: ...
def smart_setter(obj: Any) -> Callable[[str, Any], None]: ...
def temp_attributes(
    obj: Any, attrs: Dict[Any, Any], getter: Getter = ..., setter: Setter = ...
) -> ContextManager: ...
def setdefaultattr(obj: Any, name: str, value: Any) -> Any: ...
def xdir(
    obj: Any,
    getter: Callable[[Any, str], Any],
    filter: Optional[Callable[[str, Any], bool]] = None,
    _depth: int = 0,
) -> Iterable[Tuple[str, Any]]: ...
def fdir(
    obj: Any,
    getter: Optional[Callable[[Any, str], Any]] = None,
    filter: Optional[Callable[[str, Any], bool]] = None,
) -> Iterable[str]: ...

class lazy:
    def __init__(self, value: Any, *args, **kawrgs) -> None: ...
    def __call__(self) -> Any: ...

X = TypeVar("X")

def classproperty(fn: Callable[[Type[Any]], X]) -> X: ...

memoized_property = property

T = TypeVar("T")

def copy_class(
    cls: T,
    meta: Optional[Type[T]] = None,
    ignores: Optional[Sequence[str]] = None,
    new_attrs: Optional[Mapping[str, Any]] = None,
    new_name: Optional[str] = None,
) -> Type: ...
def validate_attrs(
    source: Any,
    target: Any,
    force_equals: Sequence[str] = (),
    force_differents: Sequence[str] = (),
) -> bool: ...

class SafeDataItem:
    def __init__(self, *args, **kwargs) -> None: ...
    def __get__(self, obj, owner): ...
    @staticmethod
    def slot(slot_name: str, *args, **kwargs) -> str: ...

B = TypeVar("B")
B_co = TypeVar("B_co", covariant=True)

class _FinalSubclassEnum(Protocol[B]):
    def __getattr__(self, clsname: str) -> Type[B]: ...
    __members__: Mapping[str, Type[B]]

FinalSubclassEnumeration: _FinalSubclassEnum

class DelegatedAttribute:
    def __init__(self, target_name: str, delegated_attr: str, default: Any = Unset) -> None: ...
    def __get__(self, instance, owner) -> Any: ...

def delegator(attribute: str, attrs_map: Mapping[str, str], metaclass: type = type) -> type: ...
def iter_branch_subclasses(
    cls: Type[T],
    *,
    include_this: bool = False,
    without_duplicates: bool = False,
) -> Iterator[Type[T]]: ...
def get_branch_subclasses(
    cls: Type[T],
    *,
    include_this: bool = False,
    without_duplicates: bool = False,
) -> List[Type[T]]: ...
