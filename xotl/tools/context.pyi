from typing import Any, Dict, ContextManager, TypeVar
from typing_extensions import Protocol

C = TypeVar("C")
K = TypeVar("K")
V = TypeVar("V")

class _ContextData(Dict[K, V]): ...

class _ContextProtocol(Protocol[C, K, V]):
    def __getitem__(self, key: C) -> _ContextData[K, V]: ...
    def __call__(self, key: C) -> ContextManager[_ContextData[K, V]]: ...

context: _ContextProtocol
Context: _ContextProtocol
