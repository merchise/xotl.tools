from typing import Any, ContextManager, Dict, TypeVar

from typing_extensions import Protocol

C = TypeVar("C")

class _ContextData(Dict[str, Any]): ...

class _ContextProtocol(Protocol[C]):
    def __getitem__(self, key: C) -> _ContextData: ...
    def __call__(self, key: C, **kw: Any) -> ContextManager[_ContextData]: ...

context: _ContextProtocol
Context: _ContextProtocol
