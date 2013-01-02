#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_aop
#----------------------------------------------------------------------
# Copyright (c) 2012 Medardo Rodríguez
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
# Created on Mar 26, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

__docstring_format__ = 'rst'
__author__ = 'manu'

import unittest

from datetime import timedelta
from xoutil.aop import weaved
from xoutil.aop.basic import contextualized, complementor


def days(self):
    return timedelta(days=self)


def years(self):
    return timedelta(days=365 * self)


def months(self):
    'Regards a month with 30 days'
    return timedelta(days=30 * self)


class Test(unittest.TestCase):
    def setUp(self):
        class SimpleObject(object):
            def ident(self, what):
                return what

        self.SimpleObject = SimpleObject

    def test_simple_substitution(self):
        def plusone(self, what):
            return super(_class, self).ident(what) + 1

        sobj = self.SimpleObject()
        prev = sobj.ident(99)
        with weaved(sobj, ident=plusone) as sobj:
            _class = sobj.__class__
            self.assertEqual(prev + 1, sobj.ident(99))

    def test_nested_weaved(self):
        def plusone(self, what):
            return super(_class, self).ident(what) + 1

        def plustwo(self, what):
            return super(_class2, self).ident(what) + 2

        sobj = self.SimpleObject()
        prev = sobj.ident(99)
        with weaved(sobj, ident=plusone) as sobj:
            _class = sobj.__class__
            with weaved(sobj, ident=plustwo) as sobj:
                _class2 = sobj.__class__
                self.assertEqual(prev + 3, sobj.ident(99))
            self.assertEqual(prev + 1, sobj.ident(99))
        self.assertEqual(prev, sobj.ident(99))

    def test_complementor(self):
        def __init__(self, *args, **kw):
            return self._super___init__(*args, **kw)

        def other(self):
            'Hacked'
            return self._super_other()

        @complementor(other, __init__,
                      somedict={'a': 1, 'b': 2}, somelist=range(5, 10))
        class Someclass(object):
            somedict = {'a': 0}
            somelist = range(5)

            def __init__(self, d=None, l=None):
                'My docstring'
                if d:
                    self.somedict.update(d)
                if l:
                    self.somelist.extend(l)

            def other(self):
                'Other docstring'
                return self

        ok = self.assertEqual
        ok(Someclass.somedict, {'a': 1, 'b': 2})
        ok(Someclass.somelist, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        ok(Someclass.__init__.__doc__, 'My docstring')
        ok(Someclass.other.__doc__, 'Hacked')

    def test_contextualizer(self):
        from xoutil.context import context

        class FooBazer(object):
            def inside(self):
                if context['in-context']:
                    return 'in-context'
                else:
                    return 'KABOOM'

        @contextualized(context('in-context'), FooBazer)
        class Foobar(object):
            def outside(self):
                return 'not-contextualized'

        foo = Foobar()
        self.assertEqual('in-context', foo.inside())


if __name__ == "__main__":
    unittest.main(verbosity=2)
