# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xotl.decorators
#----------------------------------------------------------------------
# Copyright (c) 2009-2011 Merchise Autrement
#
# Author: Medardo Rodriguez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


'''Some usefull decorators.'''

# TODO: reconsider all this module


from __future__ import (division as _py3_division, print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import sys

from functools import wraps, partial


curry = partial


class AttributeAlias(object):
    '''
    Descriptor to create aliases for object attributes.
    This descriptor is mainly to be used internally by "aliases" decorator. 
    '''

    def __init__(self, attr_name):
        super(AttributeAlias, self).__init__()
        self.attr_name = attr_name

    def __get__(self, instance, owner):
        return getattr(instance or owner, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance):
        delattr(instance, self.attr_name)



def settle(**kwargs):
    '''
    Return a decorator that settle different attribute values to the
    decorated target (function or class).
    '''
    def inner(target):
        for key, value in kwargs.iteritems():
            setattr(target, key, value)
        return target
    return inner



def namer(name, **kwargs):
    '''
    Similar to "settle", but always consider first argument as "name". 
    '''
    return settle(__name__=name, **kwargs)



def aliases(**kwargs):
    '''
    In a class, create an "AttributeAlias" descriptor for each definition
    as keyword argument (alias=existing_attribute).
    '''
    def inner(target):
        '''
        Direct closure decorator that settle several attribute aliases.
        '''
        assert isinstance(target, type), '"target" must be a class.'
        for alias, field in kwargs.iteritems():
            setattr(target, alias, AttributeAlias(field))
        return target
    return inner


# TODO: [manu] Review the third-party egg "decorator"
def decorator(caller):
    '''
    Eases the creation of decorators with arguments::
    
        >>> @decorator
        ... def plus(target, value):
        ...    from functools import wraps
        ...    @wraps(target)
        ...    def inner(*args):
        ...        return target(*args) + value
        ...    return inner
        
        >>> @plus(value=10)
        ... def ident(val):
        ...     return val
        
        >>> ident(1)
        11
        
    TODO: Make the decorator with default values to be callable without 
    parenthesis::
    
        >>> @decorator
        ... def plus2(func, value=1):
        ...    from functools import wraps
        ...    @wraps(func)
        ...    def inner(*args):
        ...        return func(*args) + value
        ...    return inner
        
        >>> @plus2
        ... def ident2(val):
        ...     return val
        
        >>> ident2(1)   # doctest: +SKIP
        2
    '''
    @wraps(caller)
    def outer_decorator(target=None, **kwargs):
        if len(kwargs) > 0:
            return partial(caller, **kwargs)
        else:
            return caller
    return outer_decorator


@decorator
def assignment_operator(func, maybe_inline=False):
    '''
    Makes a function that receives a name, and other args to be *assignment_operator*,
    meaning that it if its used in a single assignment statement the name will
    be taken from the left part of the ``=`` operator::
    
        >>> @assignment_operator()
        ... def test(name, *args):
        ...    return name * (len(args) + 1)
        
        >>> test('a', 1, 2)
        'aaa'
        
    (The following test fails because we can't get the source of the doctest;
    so a unit test should be provided:)
    
    ::
        >>> b = test(1, 2)    # doctest: +SKIP
        >>> b                 # doctest: +SKIP
        'bbb'
    '''
    import inspect
    import ast
    from types import FunctionType as function

    assert isinstance(func, function), '"func" must be a function.'
    @wraps(func)
    def inner(*args):
        filename, lineno, funcname, sourcecode_lines, index = inspect.getframeinfo(sys._getframe(1))
        try:
            sourceline = sourcecode_lines[index].strip()
            parsed_line = ast.parse(sourceline, filename).body[0]
            assert maybe_inline or isinstance(parsed_line, ast.Assign)
            if isinstance(parsed_line, ast.Assign):
                assert len(parsed_line.targets) == 1
                assert isinstance(parsed_line.targets[0], ast.Name)
                name = parsed_line.targets[0].id
            elif maybe_inline:
                assert isinstance(parsed_line, ast.Expr)
                name = None
            else:
                assert False
            return func(name, *args)
        except (AssertionError, SyntaxError):
            if maybe_inline:
                return func(None, *args)
            else:
                return func(*args)
        finally:
            del filename, lineno, funcname, sourcecode_lines, index
    return inner


__all__ = (b'AttributeAlias',
           b'update_wrapper',
           b'wraps',
           b'partial',
           b'settle',
           b'namer',
           b'curry',
           b'aliases',
           b'decorator',
           b'assignment_operator')


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
