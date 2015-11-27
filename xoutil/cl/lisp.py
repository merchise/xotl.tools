#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# lisp
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-25

'''Coercers equivalent to some Common Lisp forms.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from . import custom


class whether(custom):
    '''Similar to lisp "if" special form.

    If `cond` yields a valid result, do the `right` coercer, else do the rest
    of coercers in `wrongs` (optional).

    '''
    __slots__ = ()

    def __new__(cls, cond, right, *wrongs):
        from . import vouch, coercer, compose, identity_coerce, void_coerce
        cond = vouch(coercer, cond)
        if cond is identity_coerce:
            return vouch(coercer, right)
        elif cond is void_coerce:
            return compose(wrongs, default=void_coerce)
        else:
            self = super(whether, cls).__new__(cls)
            self.inner = (cond,
                          vouch(coercer, right),
                          compose(wrongs, default=void_coerce))
            return self

    def __call__(self, arg):
        from . import t
        cond, right, wrong = self.inner
        return right(arg) if t(cond(arg)) else wrong(arg)


def when(cond, *coercers):
    '''Similar to lisp "when" special form.

    If `cond` yields a valid result, do the body of `coercers`, else return
    `nil`.

    This functions uses as implementation the class `whether`:class:.

    '''
    from . import compose, void_coerce
    return whether(cond, compose(coercers, default=void_coerce))


class every(custom):
    '''Similar to lisp "every" special form.

    True if `predicate` coercer is valid of every element of sequence `arg`,
    else it returns `nil`.

    '''
    __slots__ = ()

    def __new__(cls, predicate):
        from . import vouch, coercer, identity_coerce, void_coerce
        predicate = vouch(coercer, predicate)
        if predicate is identity_coerce:
            return identity_coerce
        elif predicate is void_coerce:
            return void_coerce
        else:
            self = super(every, cls).__new__(cls)
            self.inner = predicate
            return self

    def __call__(self, arg):
        from . import t,  nil
        predicate = self.inner
        res = all(t(predicate(item)) for item in arg)
        return res if res else nil
