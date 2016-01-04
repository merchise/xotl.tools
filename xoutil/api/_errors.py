#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.api._errors
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-23

'''Internal module for API errors.

WTF: Unfortunately, exception management don't work with ABCs in Python 3.
(See issue #\ 12029_).

A mechanism compatible with all versions for this pattern could be found in
this module.

.. _12029: http://bugs.python.org/issue12029

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoutil.eight.meta import metaclass
from xoutil.eight.abc import ABC


class BaseError(Exception, ABC):
    '''Base class for all Xoutil API Exceptions.

    Allow to register concrete driver error classes in generic Xoutil
    exceptions.

    This class is an ABC in order to allow drivers to map concrete error
    classes using `adopt`:meth: method.  See `xoutil.api.error`:class:
    documentation for an example.

    '''
    pass


def is_error_class(value):
    return isinstance(value, type) and issubclass(value, BaseException)


def _is_abc_nice_with_errors():
    '''See if ABCs works nice or not in this Python version.'''
    @BaseError.adopt
    class TestError(Exception):
        pass
    try:
        raise TestError('Any msg.')
    except BaseError:
        return True
    except Exception:
        return False

_ABC_NICE_WITH_ERRORS = _is_abc_nice_with_errors()


from xoutil.tasking.lock import context_lock as _bag_assign


class ErrorBagMeta(type):
    '''Meta-class for a bag of errors that need adaption.'''
    def __new__(cls, name, bases, attrs):
        if name == 'ErrorBag' and attrs.get('__module__') == __name__:
            _super = super(ErrorBagMeta, cls).__new__
            with _bag_assign.enter():
                return _super(cls, name, bases, attrs)
        else:
            raise RuntimeError('Only one instance of errors bag is allowed.')

    def __setattr__(self, name, value):
        is_err = is_error_class(value)
        if _bag_assign.locked or not (is_err or isinstance(value, self)):
            super(ErrorBagMeta, self).__setattr__(name, value)
        else:
            if is_err:
                kind = 'layer error'
                aux = value
            else:
                kind = 'internal error descriptor'
                aux = value.wrapped
            msg = 'API {} "{}" can\'t be directly assigned.'
            raise ValueError(msg.format(kind, aux.__name__))


class ErrorBag(metaclass(ErrorBagMeta)):
    '''Singleton for API error definitions (the bag).

    Unfortunately, the ABCs mapping mechanism doesn't work for exceptions in
    some Python versions, this class define an extension could be used
    transparently if needed.

    An API Error is something declared at a generic level and is mapped to
    concrete errors in specific implementations.  See `BaseError`:class: class
    for more information.

    Don't use this class directly with its name, use instead the declared
    alias "error".

    For example::

      # myapi: In a general layer module.

      from xoutil import api
      @api.error
      class ResourceNotFoundError(BaseError):
          pass

      # --- managed-code: In any place managing this API error.

      try:
          ...
      except api.error.ResourceNotFoundError:
          # catch registered exceptions (e.g. couchdb.http.ResourceNotFound)
          pass

      # --- driver: In a concrete implementation.

      >>> import couchdb
      >>> myapi.ResourceNotFoundError.adopt(couchdb.http.ResourceNotFound)

    If the section "managed-code" is executed and inner the ``try`` part is
    raised ``couchdb.http.ResourceNotFound``, the ``except`` part is executed
    in all Python versions.  To do the magic, always define ``except`` clauses
    using API errors with `error` as a object prefix.  That is, the above
    example doesn't work in all Python versions with the next form::

      # --- managed-code: In any place managing this API error.

      ResNotFoundError = api.error.ResourceNotFoundError
      try:
          ...
      except ResNotFoundError:
          # catch registered exceptions (e.g. couchdb.http.ResourceNotFound)
          pass

    When issue #\ 12029_ is solved, it will work nicely.

    .. _12029: http://bugs.python.org/issue12029

    '''
    def __new__(cls, wrapped):
        assert cls is ErrorBag
        if is_error_class(wrapped):
            if _ABC_NICE_WITH_ERRORS:
                self = wrapped
            else:
                self = super(ErrorBag, cls).__new__(cls)
                self.wrapped = wrapped
            name = wrapped.__name__
            if not hasattr(cls, name):
                with _bag_assign.enter():
                    # to avoid direct assigning block
                    setattr(cls, name, self)
                return wrapped
            else:
                raise RuntimeError('Error "{}" already adopted.'.format(name))
        else:
            from xoutil.names import simple_name
            msg = 'Parameter `wrapped` must be an exception class, not "{}".'
            raise TypeError(msg.format(simple_name(wrapped)))

    def __init__(self, wrapped):
        pass

    def __get__(self, obj, owner):
        import sys
        if obj is None:
            assert owner is ErrorBag
            cls = sys.exc_info()[0]
            if cls is not None and issubclass(cls, self.wrapped):
                return cls
            else:
                return self.wrapped


error = ErrorBag
