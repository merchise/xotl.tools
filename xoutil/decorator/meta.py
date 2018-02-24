#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Decorator-making facilities.

This module provides a signature-keeping version of the
`xoutil.decorators.decorator`:func:, which is now deprecated in favor of this
module's version.

We scinded the decorator-making facilities from decorators per se to allow the
module `xoutil.deprecation`:mod: to be used by decorators and at the same
time, implement the decorator `~xoutil.deprecation.deprecated`:func: more
easily.


This module is an adapted work from the decorator version 3.3.2 package and is
copyright of its owner as stated below. Adaptation work is done by Merchise.

Original copyright and license notices from decorator package:

    Copyright (c) 2005-2011, Michele Simionato

    All rights reserved.

    Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.  Redistributions in
    bytecode form must reproduce the above copyright notice, this list of
    conditions and the following disclaimer in the documentation and/or other
    materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)

import sys
import re
import inspect

from functools import wraps, partial
from types import FunctionType as function

if sys.version_info[0] == 3:
    from inspect import getfullargspec as _getfullargspec
else:
    from inspect import getargspec as _getfullargspec


__all__ = ('FunctionMaker', 'flat_decorator', 'decorator')


DEF = re.compile('\s*def\s*([_\w][_\w\d]*)\s*\(')


# basic functionality
class FunctionMaker(object):
    """
    An object with the ability to create functions with a given signature.
    It has attributes name, doc, module, signature, defaults, dict and
    methods update and make.
    """
    def __init__(self, func=None, name=None, signature=None,
                 defaults=None, doc=None, module=None, funcdict=None):
        self.shortsignature = signature
        if func:
            # func can be a class or a callable, but not an instance method
            self.name = func.__name__
            if self.name == '<lambda>':  # small hack for lambda functions
                self.name = '_lambda_'
            self.doc = func.__doc__
            self.module = func.__module__
            if inspect.isfunction(func):
                argspec = _getfullargspec(func)
                for a in ('args', 'varargs', 'varkw', 'defaults', 'kwonlyargs',
                          'kwonlydefaults', 'annotations'):
                    setattr(self, a, getattr(argspec, a, None))
                for i, arg in enumerate(self.args):
                    setattr(self, 'arg%d' % i, arg)
                self.signature = inspect.formatargspec(
                    formatvalue=lambda val: "", *argspec)[1:-1]
                allargs = list(self.args)
                if self.varargs:
                    allargs.append('*' + self.varargs)
                if self.varkw:
                    allargs.append('**' + self.varkw)
                try:
                    self.shortsignature = ', '.join(allargs)
                except TypeError:
                    # exotic signature, valid only in Python 2.X
                    self.shortsignature = self.signature
                self.dict = func.__dict__.copy()
        # func=None happens when decorating a caller
        if name:
            self.name = name
        if signature is not None:
            self.signature = signature
        if defaults:
            self.defaults = defaults
        if doc:
            self.doc = doc
        if module:
            self.module = module
        if funcdict:
            self.dict = funcdict
        # check existence required attributes
        assert hasattr(self, 'name')
        if not hasattr(self, 'signature'):
            raise TypeError('You are decorating a non function: %s' % func)

    def update(self, func, **kw):
        "Update the signature of func with the data in self"
        func.__name__ = self.name
        func.__doc__ = getattr(self, 'doc', None)
        func.__dict__ = getattr(self, 'dict', {})
        func.func_defaults = getattr(self, 'defaults', ())
        func.__kwdefaults__ = getattr(self, 'kwonlydefaults', None)
        callermodule = sys._getframe(3).f_globals.get('__name__', '?')
        func.__module__ = getattr(self, 'module', callermodule)
        func.__dict__.update(kw)

    def make(self, src_templ, evaldict=None, addsource=False, **attrs):
        "Make a new function from a given template and update the signature"
        src = src_templ % vars(self)  # expand name and signature
        evaldict = evaldict or {}
        mo = DEF.match(src)
        if mo is None:
            raise SyntaxError('not a valid function template\n%s' % src)
        name = mo.group(1)  # extract the function name
        names = set([name] + [arg.strip(' *') for arg in
                              self.shortsignature.split(',')])
        for n in names:
            if n in ('_func_', '_call_'):
                raise NameError('%s is overridden in\n%s' % (n, src))
        if not src.endswith('\n'):  # add a newline just for safety
            src += '\n'   # this is needed in old versions of Python
        try:
            code = compile(src, '<string>', 'single')
            # print >> sys.stderr, 'Compiling %s' % src
            eval(code, evaldict, evaldict)
        except Exception:
            print >> sys.stderr, 'Error in generated code:'
            print >> sys.stderr, src
            raise
        func = evaldict[name]
        if addsource:
            attrs['__source__'] = src
        self.update(func, **attrs)
        return func

    @classmethod
    def create(cls, obj, body, evaldict, defaults=None,
               doc=None, module=None, addsource=True, **attrs):
        """
        Create a function from the strings name, signature and body.
        "evaldict" is the evaluation dictionary. If addsource is true an
        attribute __source__ is added to the result. The attributes attrs are
        added,
        if any.
        """
        try:
            string_types = (str, unicode)
        except NameError:
            string_types = (str,)
        if isinstance(obj, string_types):  # "name(signature)"
            obj = str(obj)
            name, rest = obj.strip().split(str('('), 1)
            signature = rest[:-1]   # strip a right parens
            func = None
        else:   # a function
            name = None
            signature = None
            func = obj
        self = cls(func, name, signature, defaults, doc, module)
        ibody = '\n'.join('    ' + line for line in body.splitlines())
        return self.make('def %(name)s(%(signature)s):\n' + ibody,
                         evaldict, addsource, **attrs)


def flat_decorator(caller, func=None):
    """
    Creates a signature keeping decorator.

    ``decorator(caller)`` converts a caller function into a decorator.

    ``decorator(caller, func)`` decorates a function using a caller.
    """
    if func is not None:    # returns a decorated function
        evaldict = func.func_globals.copy()
        evaldict['_call_'] = caller
        evaldict['_func_'] = func
        return FunctionMaker.create(
            func, "return _call_(_func_, %(shortsignature)s)",
            evaldict, undecorated=func, __wrapped__=func)
    else:   # returns a decorator
        if isinstance(caller, partial):
            return partial(decorator, caller)
        # otherwise assume caller is a function
        try:
            first = inspect.getargspec(caller)[0][0]    # first arg
            deco_sign = '%s(%s)' % (caller.__name__, first)
            deco_body = 'return flat_decorator(_call_, %s)' % first
        except IndexError:
            deco_sign = '%s()' % caller.__name__
            deco_body = 'return _call_'
        evaldict = caller.func_globals.copy()
        evaldict['_call_'] = caller
        evaldict['flat_decorator'] = evaldict['decorator'] = flat_decorator
        return FunctionMaker.create(
            deco_sign,
            deco_body,
            evaldict, undecorated=caller, __wrapped__=caller,
            doc=caller.__doc__, module=caller.__module__)
# -- End of decorators package


# FIX: This meta-decorator fails in some scenarios (old classes?)
def decorator(caller):
    '''Eases the creation of decorators with arguments.  Normally a decorator
    with arguments needs three nested functions like this::

        def decorator(*decorator_arguments):
            def real_decorator(target):
                def inner(*args, **kwargs):
                    return target(*args, **kwargs)
                return inner
            return real_decorator

    This decorator reduces the need of the first level by comprising both into
    a single function definition. However it does not removes the need for an
    ``inner`` function::

        >>> @decorator
        ... def plus(target, value):
        ...    from functools import wraps
        ...    @wraps(target)
        ...    def inner(*args):
        ...        return target(*args) + value
        ...    return inner

        >>> @plus(10)
        ... def ident(val):
        ...     return val

        >>> ident(1)
        11

    A decorator with default values for all its arguments (except, of course,
    the first one which is the decorated `target`) may be invoked
    without parenthesis::

        >>> @decorator
        ... def plus2(func, value=1, missing=2):
        ...    from functools import wraps
        ...    @wraps(func)
        ...    def inner(*args):
        ...        print(missing)
        ...        return func(*args) + value
        ...    return inner

        >>> @plus2
        ... def ident2(val):
        ...     return val

        >>> ident2(10)
        2
        11

    But (if you like) you may place the parenthesis::

        >>> @plus2()
        ... def ident3(val):
        ...     return val

        >>> ident3(10)
        2
        11

    However, this is not for free, you cannot pass a single positional argument
    which type is a function::

        >>> def p():
        ...    print('This is p!!!')

        >>> @plus2(p)   # doctest: +ELLIPSIS
        ... def dummy():
        ...    print('This is dummy')
        Traceback (most recent call last):
            ...
        TypeError: p() takes ...

    The workaround for this case is to use a keyword argument.
    '''
    @wraps(caller)
    def outer_decorator(*args, **kwargs):
        try:
            from zope.interface import Interface
        except ImportError:
            Interface = None
            # from xoutil.symbols import Unset as Interface
        if (len(args) == 1 and not kwargs and
            (isinstance(args[0], (function, type)) or
             issubclass(type(args[0]), type(Interface)))):
            # This tries to solve the case of missing () on the decorator::
            #
            #    @decorator
            #    def somedec(func, *args, **kwargs)
            #        ...
            #
            #    @somedec
            #    def decorated(*args, **kwargs):
            #        pass
            #
            # Notice, however, that this is not general enough, since we try
            # to avoid inspecting the calling frame to see if the () are in
            # place.
            func = args[0]
            return caller(func)
        elif len(args) > 0 or len(kwargs) > 0:
            def _decorator(func):
                return partial(caller, **kwargs)(*((func, ) + args))
            return _decorator
        else:
            return caller
    return outer_decorator
