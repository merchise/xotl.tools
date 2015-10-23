#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.meta
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2015-02-25

'''Implements the metaclass() function using the Py3k syntax.

'''

from . import _py3


if _py3:
    from ._meta3 import metaclass
else:
    from ._meta2 import metaclass


metaclass.__doc__ = '''Define the metaclass of a class.

    .. versionadded:: 1.4.1  But moved to this module since 1.7.0.

    This function allows to define the metaclass of a class equally in Python
    2 and 3.

    Usage::

     >>> class Meta(type):
     ...   pass

     >>> class Foobar(metaclass(Meta)):
     ...   pass

     >>> class Spam(metaclass(Meta), dict):
     ...   pass

     >>> type(Spam) is Meta
     True

     >>> Spam.__bases__ == (dict, )
     True

    .. versionadded:: 1.5.5 The `kwargs` keywords arguments with support for
       ``__prepare__``.

    Metaclasses are allowed to have a ``__prepare__`` classmethod to return
    the namespace into which the body of the class should be evaluated.  See
    :pep:`3115`.

    .. warning:: The :pep:`3115` is not possible to implement in Python 2.7.

       Despite our best efforts to have a truly compatible way of creating
       meta classes in both Python 2.7 and 3.0+, there is an inescapable
       difference in Python 2.7.  The :pep:`3115` states that ``__prepare__``
       should be called before evaluating the body of the class.  This is not
       possible in Python 2.7, since ``__new__`` already receives the
       attributes collected in the body of the class.  So it's always too late
       to call ``__prepare__`` at this point and the Python 2.7 interpreter
       does not call it.

       Our approach for Python 2.7 is calling it inside the ``__new__`` of a
       "side" metaclass that is used for the base class returned.  This means
       that ``__prepare__`` is called **only** for classes that use the
       `metaclass`:func: directly.  In the following hierarchy::

         class Meta(type):
              @classmethod
              def __prepare__(cls, name, bases, **kwargs):
                  from xoutil.collections import OrderedDict
                  return OrderedDict()

         class Foo(metaclass(Meta)):
              pass

         class Bar(Foo):
              pass

       when creating the class ``Bar`` the ``__prepare__()`` class method is
       not called in Python 2.7!

    .. seealso:: `xoutil.types.prepare_class`:func: and
       `xoutil.types.new_class`:func:.

    .. warning::

       You should always place your metaclass declaration *first* in the list
       of bases. Doing otherwise triggers *twice* the metaclass' constructors
       in Python 3.1 or less.

       If your metaclass has some non-idempotent side-effect (such as
       registration of classes), then this would lead to unwanted double
       registration of the class::

        >>> class BaseMeta(type):
        ...     classes = []
        ...     def __new__(cls, name, bases, attrs):
        ...         res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
        ...         cls.classes.append(res)   # <-- side effect
        ...         return res

        >>> class Base(metaclass(BaseMeta)):
        ...     pass

        >>> class SubType(BaseMeta):
        ...     pass

        >>> class Egg(metaclass(SubType), Base):   # <-- metaclass first
        ...     pass

        >>> Egg.__base__ is Base   # <-- but the base is Base
        True

        >>> len(BaseMeta.classes) == 2
        True

        >>> class Spam(Base, metaclass(SubType)):
        ...     'Like "Egg" but it will be registered twice in Python 2.x.'

       In this case the registration of Spam ocurred twice::

        >>> BaseMeta.classes  # doctest: +SKIP
        [<class Base>, <class Egg>, <class Spam>, <class Spam>]

       Bases, however, are just fine::

        >>> Spam.__bases__ == (Base, )
        True

    .. versionadded:: 1.7.1 Now are accepted atypical meta-classes, for
       example functions or any callable with the same arguments as those that
       type accepts (class name, tuple of base classes, attributes mapping).

'''


from re import compile
_META_STRIP = compile('(?i)(^(meta(class)?|type)_{0,2}|'
                      '_{0,2}(meta(class)?|type)$)')
del compile


def helper_class(meta, name=None, doc=None, adjust_module=True):
    '''Create a helper class based in the meta-class concept.

    :param meta: The meta-class type to base returned helper-class on it.

    :param name: The name (``__name__``) to assign to the returned
           helper-class; if None is given, a nice name is calculated.

    :param doc: The documentation (``__doc__``) to assign to the returned
           helper-class; if None is given, a nice one is calculated.

    :param adjust_module: if True, the ``__module__`` helper-class attribute
           is changed; if False is leaved unchanged.

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

    '''
    res = metaclass(meta)
    name = name or _META_STRIP.sub('', meta.__name__)
    doc = doc or ('Helper class.\n\nProvide a standard way to create `{name}`'
                  ' sub-classes using inheritance.\n\n'
                  'For example::\n\n'
                  '  class My{name}({name}):\n'
                  '      pass\n\n').format(name=name)
    res.__name__ = name
    res.__doc__ = doc
    if adjust_module:
        res.__module__ = '<helper::{}>'.format(meta.__module__)
    return res
