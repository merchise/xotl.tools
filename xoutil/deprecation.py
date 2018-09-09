#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import types
import warnings

from functools import wraps


# TODO: Invalidate this module in favor of new 'xoutil.suggest' when
# implemented

# FIX: 'warnings.warn' uses in this module 'UserWarning' instead of
# 'DeprecationWarning'.  There is a way to signal the warning with the correct
# type.

DEFAULT_MSG = ('{funcname} is now deprecated and it will be '
               'removed{in_version}. Use {replacement} instead.')


class DeprecationError(Exception):
    pass


# TODO: Use ``warnings.simplefilter('default', DeprecationWarning)``


# TODO: Maybe adapt all other functions in this module to use this descriptor.
# Currently, it's only being used in combination with xoutil.modules.customize
# to deprecate imports from xoutil top level module.
class DeprecatedImportDescriptor:
    'A descriptor that issues a deprecation warning when resolving `name`.'
    def __init__(self, replacement):
        self.attr = replacement[replacement.rfind('.') + 1:]
        self.replacement = replacement

    def __get__(self, instance, owner):
        if instance is not None:
            import warnings
            from xoutil.objects import import_object
            result = import_object(self.replacement)
            warnings.warn(
                'Importing {name} from xoutil is deprecated. '
                'You should import it from {ns}'.format(
                    name=self.attr,
                    ns=self.replacement
                ),
                UserWarning  # DeprecationWarning is silent in ipython
            )
            return result
        else:
            return self


def _nameof(item):
    '''Version of `xoutil.names.nameof`:func: to avoid importing it here.'''
    singletons = (None, True, False, Ellipsis, NotImplemented)
    res = next((str(s) for s in singletons if s is item), None)
    if res is None:
        res = '.'.join([item.__module__, item.__name__])
    return res


def deprecated(replacement, msg=DEFAULT_MSG, deprecated_module=None,
               removed_in_version=None, check_version=False, new_name=None):
    '''Small decorator for deprecated functions.

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

    '''

    def raise_if_deprecated(target, target_version):
        import pkg_resources
        string_types = (str,)
        pkg = _nameof(target)
        pkg, _obj = pkg.rsplit('.', 1)
        dist = None
        while not dist and pkg:
            try:
                dist = pkg_resources.get_distribution(pkg)
            except pkg_resources.DistributionNotFound:
                dist = None
                if '.' in pkg:
                    pkg, _obj = pkg.rsplit('.', 1)
                else:
                    pkg, _obj = None, None    # noqa
        assert dist
        if isinstance(target_version, string_types):
            target_version = pkg_resources.parse_version(target_version)
        if dist.parsed_version >= target_version:
            msg = ('A deprecated feature %r was scheduled to be '
                   'removed in version %r and it is still '
                   'alive in %r!' % (_nameof(target),
                                     str(removed_in_version),
                                     str(dist.version)))
            raise DeprecationError(msg)

    def decorator(target):
        from xoutil.eight import class_types
        target_name = new_name if new_name else target.__name__
        if deprecated_module:
            funcname = deprecated_module + '.' + target_name
        else:
            funcname = target_name
        if isinstance(replacement, class_types + (types.FunctionType, )):
            repl_name = replacement.__module__ + '.' + replacement.__name__
        else:
            repl_name = replacement
        if removed_in_version:
            in_version = ' in version ' + removed_in_version
        else:
            in_version = ''
        if isinstance(target, class_types):
            def new(*args, **kwargs):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name,
                                         in_version=in_version),
                              stacklevel=2)
                try:
                    return target.__new__(*args, **kwargs)
                except TypeError:
                    # XXX: Some classes in Python 3 don't declare an
                    # equivalent '__new__'
                    return super(result, args[0]).__new__(args[0])
            # Code copied and adapted from xoutil.objects.copy_class.  This is
            # done so because this module *must* not depends on any other,
            # otherwise an import cycle might be formed when deprecating a
            # class in xoutil.objects.
            import sys
            from xoutil.future.types import MemberDescriptorType
            meta = type(target)
            _py3 = sys.version_info[0] == 3
            td = target.__dict__
            iteritems = td.items if _py3 else td.iteritems
            attrs = {name: value
                     for name, value in iteritems()
                     if name not in ('__class__', '__mro__',
                                     '__name__', '__weakref__', '__dict__')
                     # Must remove member descriptors, otherwise the old's
                     # class descriptor will override those that must be
                     # created here.
                     if not isinstance(value, MemberDescriptorType)}
            attrs.update(__new__=new)
            result = meta(target_name, target.__bases__, attrs)
            return result
        else:
            @wraps(target)
            def inner(*args, **kw):
                if check_version and removed_in_version:
                    raise_if_deprecated(target, removed_in_version)
                warnings.warn(msg.format(funcname=funcname,
                                         replacement=repl_name,
                                         in_version=in_version),
                              stacklevel=2)
                return target(*args, **kw)
            if new_name:
                inner.__name__ = new_name
            return inner
    return decorator


def import_deprecated(module, *names, **aliases):
    '''Import functions deprecating them in the target module.

    The target module is the caller of this function (only intended to be
    called in the global part of a module).

    :param module: The module from which functions will be imported.  Could be
           a string, or an imported module.

    :param names: The names of the functions to import.

    :param aliases: Keys are the new names, values the old names.

    For example::

      >>> from xoutil.deprecation import import_deprecated
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

    '''
    from xoutil.future.types import class_types, func_types
    from xoutil.modules import force_module
    src = force_module(module)
    dst = force_module(2)
    src_name = src.__name__
    dst_name = dst.__name__
    dst = force_module(2)
    if not names and not aliases:
        # from module import *
        names = getattr(src, '__all__', None)
        if not names:
            names = (n for n in dir(src) if not n.startswith('_'))
    for name in names:
        if name not in aliases:
            aliases[name] = name
        else:
            msg = 'import_deprecated(): invalid repeated argument "{}"'
            raise ValueError(msg.format(name))
    unset = object()
    test_classes = class_types + func_types
    for alias in aliases:
        name = aliases[alias]
        target = getattr(src, name, unset)
        if target is not unset:
            if isinstance(target, test_classes):
                replacement = src_name + '.' + name
                deprecator = deprecated(replacement, DEFAULT_MSG, dst_name,
                                        new_name=alias)
                target = deprecator(target)
            setattr(dst, alias, target)
        else:
            msg = "cannot import '{}' from '{}'"
            raise ImportError(msg.format(name, src_name))


def deprecate_linked(check=None, msg=None):
    '''Deprecate an entire module if used through a link.

    This function must be called in the global context of the new module.

    :param check: Must be a module name to check, it must be part of the
           actual module name.  If not given 'xoutil.future' is assumed.

    For example::

      >>> from xoutil.deprecation import deprecate_linked
      >>> deprecate_linked()
      >>> del deprecate_linked

    '''
    import inspect
    check = check or 'xoutil.future'
    frame = inspect.currentframe().f_back
    try:
        name = frame.f_globals.get('__name__')
    finally:
        # As recommended in Python's documentation to avoid memory leaks
        del frame
    if check not in name:
        if msg is None:
            msg = ('"{}" module is now deprecated and it will be removed; use '
                   'the one in "{}" instead.').format(name, check)
        warnings.warn(msg, stacklevel=2)


def deprecate_module(replacement, msg=None):
    '''Deprecate an entire module.

    This function must be called in the global context of the deprecated
    module.

    :param replacement: The name of replacement module.

    For example::

      >>> from xoutil.deprecation import deprecate_module
      >>> deprecate_module('xoutil.symbols')
      >>> del deprecate_module

    '''
    import inspect
    frame = inspect.currentframe().f_back
    try:
        name = frame.f_globals.get('__name__')
    finally:
        # As recommended in Python's documentation to avoid memory leaks
        del frame
    if msg is None:
        msg = ('"{}" module is now deprecated and it will be removed; '
               'use "{}" instead.').format(name, replacement)
    if msg:
        warnings.warn(msg, stacklevel=2)


@deprecated(import_deprecated)
def inject_deprecated(funcnames, source, target=None):
    '''Injects a set of functions from a module into another.

    The functions will be marked as deprecated in the target module.

    :param funcnames: function names to take from the source module.

    :param source: the module where the functions resides.

    :param target: the module that will contains the deprecated functions.  If
           ``None`` will be the module calling this function.

    This function is provided for easing the deprecation of whole modules and
    should not be used to do otherwise.

    .. deprecated:: 1.8.0  Use `import_deprecated`:func:.

    '''
    from xoutil.eight import class_types
    if not target:
        import sys
        frame = sys._getframe(1)
        try:
            target_locals = frame.f_locals
        finally:
            # As recommended to avoid memory leaks
            del frame
    else:
        # FIX: @manu, there is a consistency error here, 'target_locals' is
        # never assigned
        pass
    for targetname in funcnames:
        unset = object()
        target = getattr(source, targetname, unset)
        if target is not unset:
            testclasses = (types.FunctionType, types.LambdaType) + class_types
            if isinstance(target, testclasses):
                replacement = source.__name__ + '.' + targetname
                module_name = target_locals.get('__name__', None)
                target_locals[targetname] = deprecated(replacement,
                                                       DEFAULT_MSG,
                                                       module_name)(target)
            else:
                target_locals[targetname] = target
        else:
            warnings.warn('{targetname} was expected to be in {source}'.
                          format(targetname=targetname,
                                 source=source.__name__), stacklevel=2)
