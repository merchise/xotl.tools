#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Two functions to create helper classes and mixins.

This module is in the `eight` context because these two functions depend on
several concepts that are different in Python 2 and 3.

- `helper_class`:func: creates a base class that represent a meta-class.  For
  example (only for Python 3), `xoutil.eight.abc.ABC` is different to
  `abc.ABC`::

    >>> from xoutil.eight.abc import ABC, ABCMeta
    >>> class One(ABC):
    ...     pass
    >>> One.__bases__ == (ABC, )
    False
    >>> One.__bases__ == (Mixin, )
    True

    >>> from abc import ABC
    >>> class Two(ABC):
    ...     pass
    >>> Two.__bases__ == (ABC, )
    True
    >>> Two.__bases__ == (Mixin, )
    False

- `mixin`:func: create a base-class tha consolidate several mix-ins and
  meta-classes.  For example::

    >>> from xoutil.eight.abc import ABCMeta

    >>> class One(dict):
    ...     pass

    >>> class Two(object):
    ...     pass

    >>> class OneMeta(type):
    ...     pass

    >>> class TwoMeta(type):
    ...     pass

    >>> Test = mixin(One, Two, meta=[OneMeta, TwoMeta, ABCMeta], name='Test')
    >>> Test.__name__ == 'Test'
    True
    >>> isinstance(Test, ABCMeta)
    True

These modules (this one and `meta`) must have four utilities:

- `metaclass` to use a unique syntax to declare meta-classes between Python 2
  and 3.

- `helper_class` to build a class that when used as a base impose a meta-class
  and not is found in resulting bases of defined class.  For example
  `xoutil.eight.abc.ABC`.

- `mixin` build a mixin-base composing several parts and meta-classes.

- `compose` specify the use of a mixin as one of the bases, but the new
  defined class will not be a mixin, this is not implemented yet because will
  require a big architecture re-factoring; for example::

    class Foobar(MyBase, compose(MyMixin)):
        pass

Maybe the last two names must be interchanged.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil.eight.meta import Mixin

from re import compile

_META_STRIP = compile('(?i)(^(meta(class)?|type)_{0,2}|'
                      '_{0,2}(meta(class)?|type)$)')

_MIXIN_STRIP = compile('(?i)(^mixin_{0,2}|_{0,2}mixin$)')


del compile


def helper_class(meta, name=None, meta_doc=False):
    '''Create a helper class based in the meta-class concept.

    :param meta: The meta-class type to base returned helper-class on it.

    :param name: The name (``__name__``) to assign to the returned class; if
           None is given, a nice name is calculated.

    :param meta_doc: Append `meta` documentation.

    For example::

      >>> from abc import ABCMeta
      >>> ABC = helper_class(ABCMeta)    # better than Python 3's abc.ABC :(
      >>> class MyError(Exception, ABC):
      ...     pass
      >>> (MyError.__bases__ == (Exception,), hasattr(MyError, 'register'))
      (True, True)

    This function calls `metaclass`:func: internally.  So, in the example
    anterior, `MyError` declaration is equivalent to::

      >>> class MyError(Exception, metaclass(ABCMeta)):
      ...     pass

    .. versionadded:: 1.9.7 Add parameter 'meta_doc'.

    '''
    from xoutil.eight.meta import metaclass
    res = metaclass(meta)
    doc = ('Helper class that provides a standard way to create {article} '
           '{name} using inheritance.')
    name = name or _META_STRIP.sub('', meta.__name__)
    res.__name__ = name
    article = 'an' if name[0] in "aeiouAEIOU" else 'a'
    doc = doc.format(name=name, article=article)
    if meta_doc and meta.__doc__:
        doc = '\n'.join((doc, meta.__doc__))
    res.__doc__ = doc
    if meta.__module__:
        res.__module__ = meta.__module__
    return res


def mixin(*args, **kwargs):
    '''Weave a `mixin`.

    Parameters of this function are a little tricky.

    :param name: The name of the new class created by this function.  Could be
           passed as positional or keyword argument.  Use ``__name__`` as an
           alias.  See `helper_class`:func: for more info about this parameter
           and next two.

    :param doc: Documentation of the returned mixin-class.  Could be passed as
           positional or keyword argument.  Use ``__doc__`` as an alias.


    :param module: Always given as a keyword parameter.  A string -or an
           object to be used as reference- representing the module name.  Use
           ``__module__`` as an alias.

    :param metaclass: Always given as a keyword parameter.  Could be one type
           value or a list of values (multiples meta-classes).  Use
           (``__metaclass__``, ``metaclasses``, or ``meta``) as aliases.

    If several mixins with the same base are used all-together in a class
    inheritance, Python generates ``TypeError: multiple bases have instance
    lay-out conflict``.   To avoid that, inherit from the class this function
    returns instead of desired `base`.

    '''
    from xoutil.eight.meta import metaclass
    name, doc, bases = _name_doc_and_bases(args, kwargs)
    metas = _get_metaclasses(kwargs)
    mod = _get_module(bases, kwargs)
    mod = _calc_module(mod)
    _check_repeated(kwargs)
    if metas:
        kw = {'module': mod}
        if len(metas) == 1:
            meta = metas[0]
        else:
            meta = mixin(*metas, name='MultiMixinMeta', __nobase__=True, **kw)
        bases = bases + (metaclass(meta, **kw), )
    attrs = dict(kwargs, __doc__=doc)
    if mod:
        attrs['__module__'] = mod
    res = type(name, bases, attrs)
    # Mixin.register(type(res))
    return res


def _isname(s):
    '''Determine if `s` is a `mixin` name or not.'''
    from keyword import iskeyword
    from xoutil.eight import string_types
    from xoutil.eight.string import isidentifier
    if isinstance(s, string_types):
        res = isidentifier(s)
        if not (res and iskeyword(res)):
            return res
        else:
            msg = '''Reserved keyword "{}" can't be used as name'''
            raise ValueError(msg.format(res))
    else:
        return False


def _name_doc_and_bases(args, kwargs):
    '''Extract from positional args the name, doc and bases for a mixin.'''
    from xoutil.eight import string_types
    args = list(args)
    name = None
    doc = None
    i, count = 0, len(args)
    while i < count and not doc:
        s = args[i]
        if not name:
            aux = _isname(s)
            if aux:
                name = aux
                args.pop(i)
                count -= 1
            else:
                i += 1
        elif isinstance(s, string_types):
            s = str(s).strip()
            if s:
                doc = s
                args.pop(i)
                count -= 1
            else:
                raise ValueError('Invalid empty `mixin` documentation.')
        else:
            i += 1
    bases = _get_canonical_bases(args, kwargs)
    if not name:
        name = _get_kwarg(('__name__', 'name'), kwargs)
        if name:
            name = str(name)
        else:
            if bases:
                base = bases[0]
                aux = 'Basic' if base is Mixin else base.__name__
                aux = _MIXIN_STRIP.sub('', aux)
                suffix = '_mixin' if aux[0].islower() else 'Mixin'
                name = aux + suffix
            else:
                name = 'Mixin'
    if not doc:
        doc = _get_kwarg(('__doc__', 'doc'), kwargs)
        if not doc:
            names = ', '.join(b.__name__ for b in bases if b is not Mixin)
            if names:
                doc = 'Generated mixin base from ({}).'.format(names)
                aux = bases[0].__doc__
                if aux:
                    doc += ('\n\n' + aux)
            else:
                doc = 'Generated mixin base.'
    return name, doc, bases


def _get_kwarg(keys, kwargs):
    aux = (v for v in (kwargs.pop(k, None) for k in keys) if v is not None)
    return next(aux, None)


def _check_repeated(kwargs):
    keys = ('__name__', '__doc__', 'metaclass', '__metaclass__', '__module__')
    aux = {k for k, v in ((k, kwargs.get(k)) for k in keys) if v is not None}
    if aux:
        raise ValueError('Repeated keyword arguments: {}'.format(aux))


def _get_canonical_bases(args, kwargs):
    res = []
    abm = not kwargs.pop('__nobase__', False)
    for arg in args:
        i, count = 0, len(res)
        found = False
        while not found and i < count:
            if arg in type.mro(res[i]):    # `issubclass` not used because ABCs
                found = True
            elif res[i] in type.mro(arg):
                res[i] = arg
                found = True
            else:
                i += 1
        if not found:
            res.append(arg)
        if not abm and Mixin in type.mro(arg):
            abm = False
    if abm:
        res.append(Mixin)
    return tuple(res)


def _get_metaclasses(kwargs):
    names = ('metaclass', 'meta', 'metaclasses', '__metaclass__')
    res = _get_kwarg(names, kwargs)
    if res:
        res = tuple(res) if isinstance(res, (tuple, list)) else (res, )
    return res


def _get_module(bases, kwargs):
    from xoutil.eight import string_types
    res = _get_kwarg(('module', '__module__'), kwargs)
    if res:
        if isinstance(res, string_types):
            res = str(res)
        elif isinstance(res, bool):
            aux = bases[0].__module__
            res = aux if aux != object.__module__ else None
        else:
            res = res.__module__
    return res


def _get_frame_module():
    DEPTH = 3
    try:
        from sys import _getframe
    except ImportError:
        def _getframe(arg):
            attrs = dict(f_globals={'__name__': '<mixin>'})
            return type('frame', (object,), attrs)

    return _getframe(DEPTH).f_globals.get('__name__')


def _calc_module(mod):
    from xoutil.eight import string_types as strs
    _type = isinstance(mod, type)
    if mod or _type:
        if _type:
            return mod.__module__
        elif isinstance(mod, strs):
            mod = str(mod)
            return mod.format(_get_frame_module()) if '{}' in mod else mod
        else:
            return _get_frame_module()
    else:
        return None
