#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.annotate
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on Apr 3, 2012

'''
Provides a forward-compatible (PEP 3107) annotations.
'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

__docstring_format__ = 'rst'
__author__ = 'manu'

from re import compile as _regex_compile
from ast import parse as _ast_parse
from xoutil.compat import str_base as _str_base
from xoutil.functools import partial

_ast_parse = partial(_ast_parse, filename="<annotations>", mode="eval")

from xoutil.decorator.meta import decorator
from xoutil.iterators import first

_SIGNATURE = _regex_compile(r'''(?ixm)
                            \(                # Required opening for the argumens
                            (?P<args>(.)*)
                            \)\s*             # Required close
                            (?:->\s*(?P<return>.+))?$
                            ''')

_ARG_SEP = _regex_compile(r'(?im)^\*{0,2}(?P<argname>[_\w\d]+)\s*:')


def _split_signature(signature):
    signature = (signature.strip()
                 if isinstance(signature, _str_base)
                 else '')
    if signature:
        matches = _SIGNATURE.match(signature)
        return matches.group('args'), matches.group('return')
    else:
        return '', None


def _parse_signature(signature):
    def _split_annotation_expression(expr):
        match = _ARG_SEP.match(expr)
        if not match:
            raise SyntaxError('Invalid signature expression %r' % expr)
        argname = match.group('argname')
        expr = expr[match.end():].lstrip()
        if not argname:
            raise SyntaxError('The signature %r is not valid' % expr)
        try:
            # This is a hack to help not implement an expression parser for
            # Python
            node = _ast_parse(expr)
            return argname, node, ''  # We consumed the whole expression
        except SyntaxError as error:
            # This probably will be a:
            #    ..., varname: expr...
            #                ^
            offset = error.offset
            while offset > 0 and expr[offset] != ',':
                offset -= 1
            if offset > 0 and expr[offset] == ',':
                return (argname, _ast_parse(expr[:offset]),
                        expr[offset + 1:].lstrip())
            else:
                raise

    class l(object):
        '''
        A locals implementation that skip some levels up in order to protect
        '''
        def __init__(self, init={}, skip_levels=5):
            import sys
            # XXX: This code is very fragile, but is the "right" thing to do
            #      in order not to leak implementation-related local variables.
            #      Any lower number will actually may be wrong results. For
            #      instance if skip_levels would be 2::
            #
            #          >>> args = 'args'
            #          >>> @annotate('(a: args)')
            #          ... def d():
            #          ...   pass
            #
            #      would actually get the tuple containing the string signature
            #      cause in is own implementation `annotate` uses an `args`
            #      local variable::
            #
            #          >>> d.__annotations__
            #          {u'a': (u'(a: args)',)}
            #
            # XXX: In fact, I should check that this does not create memory
            # references cycles with frames and stuff as noticed in the
            # CPython documentation; notwithstading that, python's garbage
            # collector may get rid of unreachable objects, even with loops.
            self.f = sys._getframe(skip_levels)
            self.d = dict(init)


        def __getitem__(self, key):
            from xoutil.iterators import dict_update_new
            if key in self.d:
                return self.d[key]
            else:
                while self.f and key not in self.d:
                    dict_update_new(self.d, self.f.f_locals)
                    self.f = self.f.f_back
                return self.d[key]

    args, return_annotation = _split_signature(signature)
    while args:
        arg, expr, args = _split_annotation_expression(args)
        code = compile(expr, '', 'eval')
        yield arg, eval(code, globals(), l())
    if return_annotation:
        yield 'return', eval(return_annotation, globals(), l())


@decorator
def annotate(func, signature=None, **keyword_annotations):
    '''
    Annotates a function with a forward-compatible internal form (i.e, injects
    a `__annotations__` mapping to the function.)

    You may pass the following arguments:

    - A single string with the equivalent signature of the function::

        >>> @annotate('(a: "some argument", *args: "positional arguments") -> list')
        ... def somefunction(a, *args):
        ...    pass

        >>> somefunction.__annotations__.get('a')
        'some argument'

        >>> somefunction.__annotations__.get('return') is list
        True

      In this case there are several limitations (and deviations) from the PEP
      3107 text:

      - There's no support for the full python expressions.

         - There's no support for nested arguments support (since this feature
           is also deprecated).

      - Specifying defaults is no supported (nor needed).

      - It makes no sense to put an argument without an annotation, so this
        will raise an exception (SyntaxError).

    - Several keyword arguments with each of the annotations. Since you can't
      include the 'return' keyword argument for the annotation related with the
      return of the function, we provide several alternatives: if any of the
      following keywords arguments is provided (tested in the given order):
      'return_annotation', '_return', '__return'; then it will be considered the
      'return' annotation, the rest will be regarded as other annotations.

      The previous example would be like this::

          >>> @annotate(a="some argument", args="positional arguments", return_annotation=list)
          ... def otherfunc(a, *args):
          ...    pass

          >>> otherfunc.__annotations__.get('a')
          'some argument'

          >>> otherfunc.__annotations__.get('return') is list
          True

      In any of the previous cases, you may provide more (or less) annotations
      than possible by following the PEP syntax. This is not considered an error,
      since the PEP allows annotations to be modified by others means.

      If you provide a signature string **and** keywords annotations, the keywords
      will take precedence over the signature::

          >>> @annotate('() -> list', return_annotation=tuple)
          ... def otherfunction():
          ...    pass

          >>> otherfunction.__annotations__.get('return') is list
          False

          >>> otherfunction.__annotations__.get('return') is tuple
          True

          The locals and globals in the context of the declaration are taken into
          account::

          >>> interface = object # let's mock of ourselves
          >>> class ISomething(interface):
          ...    pass

          >>> @annotate('(a: ISomething) -> ISomething')
          ... def somewhat(a):
          ...     return a

          >>> somewhat.__annotations__.get('a')     # doctest: +ELLIPSIS
          <class '...ISomething'>
          '''
    func.__annotations__ = annotations = getattr(func, '__annotations__', {})
    if signature:
        annotations.update({argname: value for argname, value in _parse_signature(signature)})
    return_annotation_kwarg = next((k for k in keyword_annotations if
                                    k in ('return_annotation', '_return',
                                          '__return')), None)
    if return_annotation_kwarg:
        annotations['return'] = keyword_annotations[return_annotation_kwarg]
        del keyword_annotations[return_annotation_kwarg]
    annotations.update(keyword_annotations)
    return func
