#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

"""A context manager for execution context flags."""

from collections.abc import Mapping, MutableMapping
from contextvars import ContextVar

from xotl.tools.future.collections import OpenDictMixin, SmartDictMixin
from xotl.tools.objects import SafeDataItem as safe

__all__ = ("Context", "context", "NullContext")


# The registry maps each active context name to a ``(handle, stack, count)``
# triple.  ``stack`` is a tuple of plain dicts, one per pushed level, bottom
# first.  ``count`` is the number of times the handle was entered.  The value
# held by the variable is never mutated in place; every change stores a new
# dict, so concurrent ``asyncio`` tasks and ``greenlets`` stay isolated.
_contexts_var: ContextVar = ContextVar("xotl.tools.contexts", default=None)


def _get_contexts():
    """Return the current registry, never the shared default."""
    result = _contexts_var.get()
    if result is None:
        return {}
    return result


class MetaContext(type(MutableMapping)):  # type: ignore
    def __len__(self):
        return sum(1 for _name, (_, _, count) in _get_contexts().items() if count > 0)

    def __iter__(self):
        return (name for name, (_, _, count) in _get_contexts().items() if count > 0)

    def __getitem__(self, name):
        entry = _get_contexts().get(name, None)
        if entry is not None:
            handle, _stack, count = entry
            if count > 0:
                return handle
        return _null_context

    def __contains__(self, name):
        """Basic support for the 'A in context' idiom."""
        return bool(self[name])


class Context(OpenDictMixin, SmartDictMixin, MutableMapping, metaclass=MetaContext):  # type: ignore
    """An execution context manager with parameters (or flags).

    Use as:

    .. doctest::

        >>> SOME_CONTEXT = object()
        >>> with context(SOME_CONTEXT):
        ...     if context[SOME_CONTEXT]:
        ...         print('In context SOME_CONTEXT')
        In context SOME_CONTEXT

    Note the difference creating the context and checking it: for entering a
    context you should use ``context(name)`` for testing whether some piece of
    code is being executed inside a context you should use ``context[name]``;
    you may also use the syntax `name in context`.

    When an existing context is re-enter, the former one is reused.
    Nevertheless, the data stored in each context is local to each level.

    For example:

    .. doctest::

        >>> with context('A', b=1) as a1:
        ...   with context('A', b=2) as a2:
        ...       print(a1 is a2)
        ...       print(a2['b'])
        ...   print(a1['b'])
        True
        2
        1

    For data access, a mapping interface is provided for all contexts. If a
    data slot is deleted at some level, upper level is used to read
    values. Each new written value is stored in current level without
    affecting upper levels.

    For example:

    .. doctest::

        >>> with context('A', b=1) as a1:
        ...   with context('A', b=2) as a2:
        ...       del a2['b']
        ...       print(a2['b'])
        1

    It is an error to *reuse* a context directly like in:

    .. doctest::

        >>> with context('A', b=1) as a1:   # doctest: +ELLIPSIS
        ...   with a1:
        ...       pass
        Traceback (most recent call last):
        ...
        RuntimeError: Entering the same context level twice! ...

    Isolation between concurrent ``asyncio`` tasks and ``greenlets`` is granted
    by `contextvars`:mod:; each task sees the contexts active where it was
    created, and nested entries never leak back to the parent.

    .. versionchanged:: 3.4.0 Reimplemented over `contextvars`:mod: replacing the
       ``threading.local`` and greenlet-local shims.

    """

    __slots__ = (
        "name",
        safe.slot(OpenDictMixin.__cache_name__, dict),
    )

    def __new__(cls, name, **data):
        contexts = _get_contexts()
        entry = contexts.get(name, None)
        if entry is not None:
            self, stack, count = entry
            new_stack = stack + (dict(data),)
            new_contexts = dict(contexts)
            new_contexts[name] = (self, new_stack, count)
            _contexts_var.set(new_contexts)
            return self
        else:
            self = super().__new__(cls)
            object.__setattr__(self, "name", name)
            new_contexts = dict(contexts)
            new_contexts[name] = (self, (dict(data),), 0)
            _contexts_var.set(new_contexts)
            # TODO: Redefine all event management
            return self

    @classmethod
    def from_dicts(cls, ctx, overrides=None, defaults=None):
        """Creates a context introducing both defaults and overrides.

        This combines both the standard constructor and `from_defaults`:meth:.

        If the same key appears in both `overrides` and `defaults`, ignore the
        default.

        """
        if not overrides:
            overrides = {}
        if not defaults:
            defaults = {}
        current = cls[ctx]
        current_attrs = dict(current) if current else {}
        attrs = dict(defaults, **current_attrs)
        attrs.update(overrides)
        return cls(ctx, **attrs)

    @classmethod
    def from_defaults(cls, ctx, **defaults):
        """Creates context `ctx` introducing only new keys given in `defaults`.

        The normal behavior when you enter a new level in the context is to
        override the values with the new one.

        Example:

           >>> with context.from_defaults('A', a=1):
           ...    with context.from_defaults('A', a=2, b=1) as c:
           ...        assert c['a'] == 1

        """
        return cls.from_dicts(ctx, defaults=defaults)

    def __init__(self, *args, **kwargs):
        """Must be defined empty for `__new__` parameters compatibility.

        Using generic parameters definition allow any redefinition of this
        class can use this `__init__`.

        """

    def _entry(self):
        """Return the ``(stack, count)`` pair for this handle.

        The handle is considered inactive when the registry holds no entry
        for its name, or the entry belongs to a different handle object, or
        the entry was pushed but not yet entered.  Inactive handles behave
        like empty mappings.

        """
        try:
            name = object.__getattribute__(self, "name")
        except AttributeError:
            return ((), 0)
        entry = _get_contexts().get(name, None)
        if entry is None:
            return ((), 0)
        handle, stack, count = entry
        if handle is not self:
            return ((), 0)
        return (stack, count)

    def _store(self, stack, count):
        """Store a new ``(stack, count)`` pair for this handle.

        Both the registry dict and the stack tuple are copied, so values
        already observed in another task or greenlet are never mutated.

        """
        name = object.__getattribute__(self, "name")
        new_contexts = dict(_get_contexts())
        new_contexts[name] = (self, tuple(stack), count)
        _contexts_var.set(new_contexts)

    def _remove(self):
        name = object.__getattribute__(self, "name")
        new_contexts = dict(_get_contexts())
        new_contexts.pop(name, None)
        _contexts_var.set(new_contexts)

    @property
    def count(self):
        """Number of times this context level was entered."""
        _stack, count = self._entry()
        return count

    @property
    def level(self):
        """Number of pushed levels for this context."""
        stack, _count = self._entry()
        return len(stack)

    def __call__(self, **data):
        """Allow re-enter in a new level to an already assigned context."""
        self.push_level(**data)
        return self

    def __nonzero__(self):
        return bool(self.count)

    __bool__ = __nonzero__

    def push_level(self, *args, **kwargs):
        """Push a new level filled with `args` and `kwargs`.

        Returns the pushed `level` number.

        """
        new_level = {}
        for arg in args:
            if hasattr(arg, "keys"):
                for key in arg.keys():
                    new_level[key] = arg[key]
            else:
                for key, value in arg:
                    new_level[key] = value
        new_level.update(kwargs)
        stack, count = self._entry()
        new_stack = tuple(stack) + (new_level,)
        self._store(new_stack, count)
        return len(new_stack)

    def pop_level(self):
        """Pop the last pushed level and return it.

        Raises TypeError when there are no levels.

        """
        stack, count = self._entry()
        if not stack:
            raise TypeError("Cannot pop from Context without any levels")
        self._store(tuple(stack[:-1]), count)
        return dict(stack[-1])

    def peek(self):
        """Return a copy of the top-most level without lower level keys."""
        stack, _count = self._entry()
        if not stack:
            raise TypeError("Cannot peek a Context without any levels")
        return dict(stack[-1])

    def __enter__(self):
        stack, count = self._entry()
        if count + 1 == len(stack):
            self._store(stack, count + 1)
            return self
        else:
            msg = "Entering the same context level twice! -- c(%s, %d, %d)"
            raise RuntimeError(msg % (self.name, count, len(stack)))

    def __exit__(self, exc_type, exc_value, traceback):
        stack, count = self._entry()
        if count <= 0:
            raise RuntimeError("Exiting a context that was not entered -- c(%s)" % (self.name,))
        new_stack = tuple(stack[:-1])
        if count == 1:
            self._remove()
        else:
            self._store(new_stack, count - 1)
        return False

    def __len__(self):
        return sum(1 for _key in self.__iter__())

    def __iter__(self):
        stack, _count = self._entry()
        seen = set()
        result = []
        for level in reversed(stack):
            for key in level:
                if key not in seen:
                    seen.add(key)
                    result.append(key)
        return iter(result)

    def __getitem__(self, key):
        stack, _count = self._entry()
        for level in reversed(stack):
            if key in level:
                return level[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        stack, count = self._entry()
        if not stack:
            raise KeyError(key)
        new_top = dict(stack[-1])
        new_top[key] = value
        self._store(tuple(stack[:-1]) + (new_top,), count)

    def __delitem__(self, key):
        stack, count = self._entry()
        if not stack or key not in stack[-1]:
            raise KeyError(key)
        new_top = dict(stack[-1])
        del new_top[key]
        self._store(tuple(stack[:-1]) + (new_top,), count)

    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return "%s(%s)" % (type(self).__name__, str(self))


# A simple alias for Context
context = Context


class NullContext(Mapping):
    """Singleton context to be used (returned) as default when no one is
    defined.

    """

    __slots__ = ()

    instance = None
    name = ""

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())

    def __getitem__(self, key):
        raise KeyError(key)

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__

    def __enter__(self):
        return _null_context

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def get(self, name, default=None):
        return default

    @property
    def level(self):
        return 0


_null_context = NullContext()
