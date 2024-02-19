#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import types
import warnings
from functools import wraps

from typing_extensions import deprecated as stdlib_deprecated

DEFAULT_MSG = (
    "{funcname} is now deprecated and it will be removed{in_version}. Use {replacement} instead."
)


class DeprecationError(Exception):
    pass


# TODO: Use ``warnings.simplefilter('default', DeprecationWarning)``


# TODO: Maybe adapt all other functions in this module to use this descriptor.
# Currently, it's only being used in combination with
# xotl.tools.modules.customize to deprecate imports from xotl.tools top level
# module.
class DeprecatedImportDescriptor:
    "A descriptor that issues a deprecation warning when resolving `name`."

    def __init__(self, replacement):
        self.attr = replacement[replacement.rfind(".") + 1 :]
        self.replacement = replacement

    def __get__(self, instance, owner):
        if instance is not None:
            import warnings

            from xotl.tools.objects import import_object

            result = import_object(self.replacement)
            warnings.warn(
                f"Importing {self.attr} from xotl.tools is deprecated. "
                f"You should import it from {self.replacement}",
                DeprecationWarning,
                stacklevel=3,
            )
            return result
        else:
            return self


def _nameof(item):
    "Version of `xotl.tools.names.nameof`:func: to avoid importing it here."
    singletons = (None, True, False, Ellipsis, NotImplemented)
    res = next((str(s) for s in singletons if s is item), None)
    if res is None:
        res = ".".join([item.__module__, item.__name__])
    return res


@stdlib_deprecated("Use warnings.deprecated or typing_extensions.deprecated")
def deprecated(
    replacement,
    msg=DEFAULT_MSG,
    deprecated_module=None,
    removed_in_version=None,
    check_version=False,
    new_name=None,
):
    """Small decorator for deprecated functions.

    Usage::

        @deprecated(new_function)
        def deprecated_function(...):
            ...

    :param replacement: Either a string or the object that replaces the
       deprecated.

    :param msg: A deprecation warning message template.  You should provide
       keyword arguments for the `format`:func: function.  Currently we pass
       the current keyword arguments: `replacement` (after some processing),
       `funcname` with the name of the currently deprecated object and
       `in_version` with the version this object is going to be removed if
       `removed_in_version` argument is not None.

       Defaults to: "{funcname} is now deprecated and it will be
       removed{in_version}.  Use {replacement} instead."

    :param removed_in_version: The version the deprecated object is going to be
       removed.

    :param check_version: If True and `removed_in_version` is not None, then
       declarations of obseleted objects will raise a DeprecationError.  This
       helps the release manager to keep the release clean.

       .. note:: Currently only works with setuptools' installed distributions.

    :param deprecated_module: If provided, the name of the module the
       deprecated object resides.  Not needed if the deprecated object is a
       function or class.

    :param new_name: If provided, it's used as the name of the
       deprecated object.  Needed to allow renaming in
       `import_deprecated`:func: helper function.

    .. note:: Deprecating some classes in Python 3 could fail.  This is
       because those classes do not declare a '__new__' par of the declared
       '__init__'.  The problem is solved if the '__new__' of the super-class
       has no arguments.  This doesn't happen in Python 2.

       To solve these cases mark the deprecation in a comment and issue the
       warning directly in the constructor code.

    .. versionchanged:: 1.4.1 Introduces removed_in_version and check_version.

    .. versionchanged:: 2.2.6 Use DeprecationWarning instead of UserWarning.

    .. deprecated:: 3.0.0

    """

    def raise_if_deprecated(target, target_version):
        from importlib import metadata
        from importlib.metadata import PackageNotFoundError

        from packaging.version import parse as parse_version

        pkg = _nameof(target)
        pkg, _obj = pkg.rsplit(".", 1)
        dist = None
        while not dist and pkg:
            try:
                dist = metadata.distribution(pkg)
            except PackageNotFoundError:
                dist = None
                if "." in pkg:
                    pkg, _obj = pkg.rsplit(".", 1)
                else:
                    pkg, _obj = None, None  # noqa
        assert dist
        if isinstance(target_version, str):
            target_version = parse_version(target_version)

        if parse_version(dist.version) >= target_version:
            msg = (
                f"A deprecated feature {_nameof(target)} was scheduled to be "
                f"removed in version {removed_in_version} and it is still "
                f"alive in {dist.version}"
            )
            raise DeprecationError(msg)

    def decorator(target):
        target_name = new_name if new_name else target.__name__
        if deprecated_module:
            funcname = deprecated_module + "." + target_name
        else:
            funcname = target_name
        if isinstance(replacement, (type, types.FunctionType)):
            repl_name = replacement.__module__ + "." + replacement.__name__
        else:
            repl_name = replacement
        if removed_in_version:
            in_version = " in version " + removed_in_version
        else:
            in_version = ""
        if isinstance(target, type):

            def new(*args, **kwargs):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(
                    msg.format(
                        funcname=funcname,
                        replacement=repl_name,
                        in_version=in_version,
                    ),
                    stacklevel=2,
                )
                try:
                    return target.__new__(*args, **kwargs)
                except TypeError:
                    # XXX: Some classes in Python 3 don't declare an
                    # equivalent '__new__'
                    return super(result, args[0]).__new__(args[0])

            # Code copied and adapted from xotl.tools.objects.copy_class.
            # This is done so because this module *must* not depends on any
            # other, otherwise an import cycle might be formed when
            # deprecating a class in xotl.tools.objects.
            from xotl.tools.future.types import MemberDescriptorType

            meta = type(target)
            td = target.__dict__
            iteritems = td.items
            attrs = {
                name: value
                for name, value in iteritems()
                if name not in _DUNDER_ATTRS
                # Must remove member descriptors, otherwise the old's
                # class descriptor will override those that must be
                # created here.
                if not isinstance(value, MemberDescriptorType)
            }
            attrs.update(__new__=new)
            result = meta(target_name, target.__bases__, attrs)
            return result
        else:

            @wraps(target)
            def inner(*args, **kw):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(
                    msg.format(funcname=funcname, replacement=repl_name, in_version=in_version),
                    stacklevel=2,
                )
                return target(*args, **kw)

            if new_name:
                inner.__name__ = new_name
            return inner

    return decorator


@stdlib_deprecated("Use warnings.deprecated or typing_extensions.deprecated")
def import_deprecated(module, *names, **aliases):
    """Import functions deprecating them in the target module.

    The target module is the caller of this function (only intended to be
    called in the global part of a module).

    :param module: The module from which functions will be imported.  Could be
           a string, or an imported module.

    :param names: The names of the functions to import.

    :param aliases: Keys are the new names, values the old names.

    For example::

      >>> from xotl.tools.deprecation import import_deprecated
      >>> import math
      >>> import_deprecated(math, 'sin', new_cos='cos')
      >>> sin is not math.sin
      True

    Next examples are all ``True``, but them print the deprecation warning
    when executed::

      >>> sin(math.pi/2) == 1.0
      >>> new_cos(2*math.pi) == math.cos(2*math.pi)

    If no identifier is given, it is assumed equivalent as ``from module
    import *``.

    The statement ``import_deprecated('math', 'sin', new_cos='cos')`` has the
    same semantics as ``from math import sin, cos as new_cos``, but
    deprecating current module symbols.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.

    .. deprecated:: 3.0.0

    """
    from xotl.tools.future.types import func_types
    from xotl.tools.modules import force_module

    src = force_module(module)
    dst = force_module(2)
    src_name = src.__name__
    dst_name = dst.__name__
    dst = force_module(2)
    if not names and not aliases:
        names = getattr(src, "__all__", None)
        if not names:
            names = (n for n in dir(src) if not n.startswith("_"))
    for name in names:
        if name not in aliases:
            aliases[name] = name
        else:
            msg = 'import_deprecated(): invalid repeated argument "{}"'
            raise ValueError(msg.format(name))
    unset = object()
    test_classes = func_types + (type,)
    for alias in aliases:
        name = aliases[alias]
        target = getattr(src, name, unset)
        if target is not unset:
            if isinstance(target, test_classes):
                replacement = src_name + "." + name
                deprecator = deprecated(replacement, DEFAULT_MSG, dst_name, new_name=alias)
                target = deprecator(target)
            setattr(dst, alias, target)
        else:
            msg = "cannot import '{}' from '{}'"
            raise ImportError(msg.format(name, src_name))


@stdlib_deprecated("Use warnings.deprecated or typing_extensions.deprecated")
def deprecate_linked(check=None, msg=None):
    """Deprecate an entire module if used through a link.

    This function must be called in the global context of the new module.

    :param check: Must be a module name to check, it must be part of the
           actual module name.  If not given 'xotl.tools.future' is assumed.

    For example::

      >>> from xotl.tools.deprecation import deprecate_linked
      >>> deprecate_linked()
      >>> del deprecate_linked

    .. deprecated:: 3.0.0

    """
    import inspect

    check = check or "xotl.tools.future"
    frame = inspect.currentframe().f_back
    try:
        name = frame.f_globals.get("__name__")
    finally:
        # As recommended in Python's documentation to avoid memory leaks
        del frame
    if check not in name:
        if msg is None:
            msg = (
                '"{}" module is now deprecated and it will be removed; use '
                'the one in "{}" instead.'
            ).format(name, check)
        warnings.warn(msg, stacklevel=2)


@stdlib_deprecated("Use warnings.deprecated or typing_extensions.deprecated")
def deprecate_module(replacement, msg=None):
    """Deprecate an entire module.

    This function must be called in the global context of the deprecated
    module.

    :param replacement: The name of replacement module.

    For example::

      >>> from xotl.tools.deprecation import deprecate_module
      >>> deprecate_module('xotl.tools.symbols')
      >>> del deprecate_module

    .. deprecated:: 3.0.0

    """
    import inspect

    frame = inspect.currentframe().f_back
    try:
        name = frame.f_globals.get("__name__")
    finally:
        # As recommended in Python's documentation to avoid memory leaks
        del frame
    if msg is None:
        msg = ('"{}" module is now deprecated and it will be removed; ' 'use "{}" instead.').format(
            name, replacement
        )
    if msg:
        warnings.warn(msg, stacklevel=2)


_DUNDER_ATTRS = {
    "__class__",
    "__dict__",
    "__mro__",
    "__name__",
    "__weakref__",
}
