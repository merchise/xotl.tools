#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.aop.classical
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Apr 26, 2012

'''
This module provides a very simple and classical way to weaved whole classes
with "aspect classes". 

This "classical" approach is different from the basic approach in
:mod:`xoutil.aop.basic`_ in that this one is meant to apply lasting changes to
the behavior of objects without regarding the local context of the object.

An aspect class is normal class with some attributes and methods, when you weave
an aspect class into another normal class:

- Every attribute (non-method, basically non-callable) gets updated/appended in 
  the original class.
  
- Any method defined in the aspect class that is neither an `advice method`_,
  an `after method`_, nor a `before method`_ is simply injected in the original
  class.
  
.. _after method:

- You may create an after method by either using the ``@after`` decorator or by
  using the name convention ``after_<original_metho_name>``. 
  
  Every after method gets called after the original (unweaved) methods. Any
  after method should have the signature::
  
      after(self, method_description, result, exc_value=None)
      
  The ``result`` parameter contains the result of the original method or
  ``None``. 
  
  The ``method_description`` is always an instance of
  :class:`MethodDescriptor`_.
  
  The ``exc_value`` parameter is not None to indicate that an exception was
  raised by the original method. In that case it will be the exception raised.
  You may change the exception to another one, by raising another exception
  (please use the chaining of exceptions if you can). If you raise
  StopExceptionChain the exception is not propagated to the calling code.
  
  ``self`` will contain (a proxy to) the instance of the original class.
  
  .. warning::
  
     After methods should return the result of the original method, or another
     suitable value. If you forget to return a value you may broke clients that
     depend on the original class.
      
.. _before method:

- You may provide a before method by either using the @before decorator or by 
  using the name convention ``before_<original_method_name>``.
  
  Similar to the previous but called before the original method::
  
      before(self, method_description)
      
  Notice you also receive an ``exc_value`` argument because several aspects may
  be weaved into a single class. In the case that a before method raises an
  exception, the original method won't be called and the exception is
  propagated; notice this also makes that before/after methods defined in the
  same aspect class for the same method won't be called.
  
.. _advice method:

- Advice or around methods
  
  
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil.functools import wraps

__docstring_format__ = 'rst'
__author__ = 'manu'


class StopExceptionChain(Exception):
    pass


class _AspectType(type):
    def __new__(cls, name, bases, members):
        def transform(member_name, member_value):
            if (callable(member_value) and
                (member_name.startswith(b'after_') or
                 member_name.startswith(b'before_') or
                 member_name.startswith(b'around_'))):
                result = staticmethod(member_value)
            else:
                result = member_value
            return result
        
        _super = super(_AspectType, cls).__new__
        return _super(cls,
                      name,
                      bases,
                      {name: transform(name, value)
                            for name, value in members.items()})

class AspectBaseFragment(object):
    '''
    A convenient base class for aspects fragments [*]_.
    
    .. [*] The concept of an aspect fragment is due to the reasoning that it is
           thought that the weaving of an aspect may be structured in several
           layers, each considering the targets of the weaving process. So it
           may be easier to weave an aspect that is fragmented in little
           classes.
    '''
    __metaclass__ = _AspectType



def _weave_after_method(cls, aspect, method_name,
                        after_method_name='after_{method_name}'):
    '''
    Tries to weave an after method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`cls`.
    
    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s.
    
        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what
        
        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)/what
        
        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0
        
        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero
        
    Now, let's define a simple class that defines an after_echo
    **staticmethod** and weave the previous classes::
    
        >>> class Logging(object):
        ...    @staticmethod
        ...    def after_echo(self, method_desc, result, exc_value):
        ...        if not exc_value:
        ...            print('Method {m} returned {result!r}'.format(m=method_desc, result=result))
        ...        else:
        ...            print('When calling method {m}, {exc!r} was raised!'.format(m=method_desc, exc=exc_value))
        ...        return result
        
        >>> _weave_after_method(GoodClass, Logging, 'echo')
        >>> _weave_after_method(BadClass, Logging, 'echo')
        
    After weaving every instance (even those that already exists) will behave
    with the new funcionality included::
    
        >>> good_instance.echo(0)       # doctest: +ELLIPSIS
        Method <...> returned 0
        0
        
        # You won't see the print result cause the Exception in doctests.
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero
        
    You may define another 'aspect' elsewhere an weave it on top::
    
        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'respond': ['echo'], }, 'anon': {}}
        ...    
        ...    @staticmethod
        ...    def after_echo(self, method_desc, result, exc_value):
        ...        if Security.current_user_mayrespond('echo'):
        ...            return result
        ...
        ...    @classmethod
        ...    def current_user_mayrespond(cls, method):
        ...        current_user = cls.get_current_user()
        ...        if current_user in cls.__perms__:
        ...            perms = cls.__perms__.setdefault(current_user, {})
        ...            respond_perms = perms.setdefault('respond', [])
        ...            return method in respond_perms
        ...        else:
        ...            return False
        ...
        ...    @classmethod
        ...    def get_current_user(cls):
        ...        return cls.current_user
        
        >>> _weave_after_method(GoodClass, Security, 'echo')
        
        >>> good_instance.echo(0)        # doctest: +ELLIPSIS
        Method <...> returned 0
        0
        
        # Changing the current user to other than 'manu', has the effect that
        # the Security aspect does not allow to return a response.
        >>> Security.current_user = 'other'
        >>> good_instance.echo(0)        # doctest: +ELLIPSIS
        Method <...> returned 0
    '''
    method = getattr(cls, method_name)
    after_method = getattr(aspect,
                           after_method_name.format(method_name=method_name))

    def inner(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
        except Exception as error:
            result = None
            exc_value = error
        else:
            exc_value = None
        try:
            # TODO: create the method description with the calling arguments
            result = after_method(self, method, result, exc_value)
            if exc_value:
                # TODO: include __traceback__ weakref
                raise exc_value
            else:
                return result
        except StopExceptionChain:
            pass

    if method and after_method:
        wrapped = wraps(method)(inner)
        wrapped._merchise_after_method = True
        setattr(cls, method_name, wrapped)

def _weave_before_method(cls, aspect, method_name,
                         before_method_name='before_{method_name}'):
    '''
    Tries to weave a before method given by :param:`method_name` defined (by
    name convention) in :param:`aspect` into the class :param:`cls`.
    
    The following two classes define a single method `echo`. The second class
    may raise `ZeroDivisionError`s.
    
        >>> class GoodClass(object):
        ...    def echo(self, what):
        ...        return what
        
        >>> class BadClass(object):
        ...    def echo(self, what):
        ...        return (what+1)/what
        
        >>> good_instance = GoodClass()
        >>> good_instance.echo(0)
        0
        
        >>> bad_instance = BadClass()
        >>> bad_instance.echo(0)
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero
    
    The following class defines a Security aspect that allows the execution of
    methods by user::
    
        >>> class Security(object):
        ...    current_user = 'manu'
        ...    __perms__ = {'manu': {'execute': ['echo'], }, 'anon': {}}
        ...    
        ...    @staticmethod
        ...    def check_execution_permissions(self, method_desc):
        ...        from xoutil.objects import nameof
        ...        if Security.current_user_may_execute(nameof(method_desc)):
        ...            return result
        ...
        ...    @classmethod
        ...    def current_user_may_execute(cls, method):
        ...        current_user = cls.get_current_user()
        ...        if current_user in cls.__perms__:
        ...            perms = cls.__perms__.setdefault(current_user, {})
        ...            respond_perms = perms.setdefault('execute', [])
        ...            if method not in respond_perms:
        ...                raise Exception('Forbidden')
        ...        else:
        ...            raise Exception('Forbidden')
        ...
        ...    @classmethod
        ...    def get_current_user(cls):
        ...        return cls.current_user
        
    Now let's apply our security aspect::
    
        >>> _weave_before_method(GoodClass, Security, 'echo', 'check_execution_permissions')
        >>> _weave_before_method(BadClass, Security, 'echo', 'check_execution_permissions')
        
    Now 'manu' may still execute the 'echo' method for both GoodClass and
    BadClass instances::
    
        >>> good_instance.echo(1)
        1
        
        >>> bad_instance.echo(1)
        2
        
    Other users are not allowed::
    
        >>> Security.current_user = 'other'
        >>> bad_instance.echo(0) # If allowed it would raise a ZeroDivisionError
        Traceback (most recent call last):
            ...
        Exception: Forbidden
        
        
    '''
    method = getattr(cls, method_name)
    before_method = getattr(aspect, before_method_name.format(method_name=method_name))

    def inner(self, *args, **kwargs):
        # TODO: create the method description with the calling arguments
        result = before_method(self, method)
        return method(self, *args, **kwargs) or result

    if method and before_method:
        wrapped = wraps(method)(inner)
        wrapped._merchise_before_method = True
        setattr(cls, method_name, wrapped)


