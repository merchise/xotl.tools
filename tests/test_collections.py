#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_collections
#----------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Jul 3, 2012


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)
import sys
import unittest
from random import shuffle

try:
    import pytest
except:
    class pytest(object):
        class _mark(object):
            def __getattr__(self, attr):
                return lambda *a, **kw: (lambda f: f)
        mark = _mark()

from xoutil.collections import defaultdict


class TestCollections(unittest.TestCase):
    def test_defaultdict(self):
        d = defaultdict(lambda key, d: 'a')
        self.assertEqual('a', d['abc'])
        d['abc'] = 1
        self.assertEqual(1, d['abc'])


def test_stacked_dict():
    from xoutil.collections import StackedDict
    sd = StackedDict(a='level-0')
    assert sd.peek() == dict(a='level-0')
    sd.push(a=1, b=2, c=10)
    assert sd.level == 1
    assert sd.peek() == dict(a=1, b=2, c=10)
    sd.push(b=4, c=5)
    assert sd.peek() == dict(b=4, c=5)
    assert sd.level == 2
    assert sd['b'] == 4
    assert sd['a'] == 1
    assert sd['c'] == 5
    assert len(sd) == 3
    del sd['c']
    try:
        del sd['c']
        assert False, 'Should have raise KeyError'
    except KeyError:
        pass
    except:
        assert False, 'Should have raise KeyError'
    assert sd.pop() == {'b': 4}
    assert sd['b'] == 2
    assert sd['a'] == 1
    assert len(sd) == 3
    sd.pop()
    assert sd['a'] == 'level-0'
    try:
        sd.pop()
        assert False, 'Level 0 cannot be poped. It should have raised a TypeError'
    except TypeError:
        pass
    except:
        assert False, 'Level 0 cannot be poped. It should have raised a TypeError'


# Backported from Python 3.3.0 standard library
from xoutil.six import PY3
from xoutil.collections import ChainMap, Counter, OrderedDict, Mapping
from xoutil.collections import MutableMapping
import copy, pickle, inspect
from random import randrange

class TestChainMap(unittest.TestCase):
    def test_basics(self):
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        d = c.new_child()
        d['b'] = 20
        d['c'] = 30
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertEqual(d.items(), dict(a=1, b=20, c=30).items())    # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        for key in 'abc':                                             # check contains
            self.assertIn(key, d)
        for k, v in dict(a=1, b=20, c=30, z=100).items():             # check get
            self.assertEqual(d.get(k, 100), v)

        del d['b']                                                    # unmask a value
        self.assertEqual(d.maps, [{'c':30}, {'a':1, 'b':2}])          # check internal state
        self.assertEqual(d.items(), dict(a=1, b=2, c=30).items())     # check items/iter/getitem
        self.assertEqual(len(d), 3)                                   # check len
        for key in 'abc':                                             # check contains
            self.assertIn(key, d)
        for k, v in dict(a=1, b=2, c=30, z=100).items():              # check get
            self.assertEqual(d.get(k, 100), v)
        if not PY3:
            self.assertIn(repr(d), [                                      # check repr
                type(d).__name__ + "({u'c': 30}, {u'a': 1, u'b': 2})",
                type(d).__name__ + "({u'c': 30}, {u'b': 2, u'a': 1})"
            ])
        else:
            self.assertIn(repr(d), [                                      # check repr
                type(d).__name__ + "({'c': 30}, {'a': 1, 'b': 2})",
                type(d).__name__ + "({'c': 30}, {'b': 2, 'a': 1})"
            ])


        for e in d.copy(), copy.copy(d):                               # check shallow copies
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            self.assertIsNot(d.maps[0], e.maps[0])
            for m1, m2 in zip(d.maps[1:], e.maps[1:]):
                self.assertIs(m1, m2)

        for e in [pickle.loads(pickle.dumps(d)),
                  copy.deepcopy(d),
                  eval(repr(d))
                ]:                                                    # check deep copies
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            for m1, m2 in zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)

        f = d.new_child()
        f['b'] = 5
        self.assertEqual(f.maps, [{'b': 5}, {'c':30}, {'a':1, 'b':2}])
        self.assertEqual(f.parents.maps, [{'c':30}, {'a':1, 'b':2}])   # check parents
        self.assertEqual(f['b'], 5)                                    # find first in chain
        self.assertEqual(f.parents['b'], 2)                            # look beyond maps[0]

    def test_contructor(self):
        self.assertEqual(ChainMap().maps, [{}])                        # no-args --> one new dict
        self.assertEqual(ChainMap({1:2}).maps, [{1:2}])                # 1 arg --> list

    def test_bool(self):
        self.assertFalse(ChainMap())
        self.assertFalse(ChainMap({}, {}))
        self.assertTrue(ChainMap({1:2}, {}))
        self.assertTrue(ChainMap({}, {1:2}))

    def test_missing(self):
        class DefaultChainMap(ChainMap):
            def __missing__(self, key):
                return 999
        d = DefaultChainMap(dict(a=1, b=2), dict(b=20, c=30))
        for k, v in dict(a=1, b=2, c=30, d=999).items():
            self.assertEqual(d[k], v)                                  # check __getitem__ w/missing
        for k, v in dict(a=1, b=2, c=30, d=77).items():
            self.assertEqual(d.get(k, 77), v)                          # check get() w/ missing
        for k, v in dict(a=True, b=True, c=True, d=False).items():
            self.assertEqual(k in d, v)                                # check __contains__ w/missing
        self.assertEqual(d.pop('a', 1001), 1, d)
        self.assertEqual(d.pop('a', 1002), 1002)                       # check pop() w/missing
        self.assertEqual(d.popitem(), ('b', 2))                        # check popitem() w/missing
        with self.assertRaises(KeyError):
            d.popitem()

    def test_dict_coercion(self):
        d = ChainMap(dict(a=1, b=2), dict(b=20, c=30))
        self.assertEqual(dict(d), dict(a=1, b=2, c=30))
        self.assertEqual(dict(d.items()), dict(a=1, b=2, c=30))

    def test_new_child(self):
        'Tests for changes for issue #16613.'
        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = {'b':20, 'c': 30}
        d = c.new_child(m)
        self.assertEqual(d.maps, [{'b':20, 'c':30}, {'a':1, 'b':2}])  # check internal state
        self.assertIs(m, d.maps[0])

        # Use a different map than a dict
        class lowerdict(dict):
            def __getitem__(self, key):
                if isinstance(key, str):
                    key = key.lower()
                return dict.__getitem__(self, key)
            def __contains__(self, key):
                if isinstance(key, str):
                    key = key.lower()
                return dict.__contains__(self, key)

        c = ChainMap()
        c['a'] = 1
        c['b'] = 2
        m = lowerdict(b=20, c=30)
        d = c.new_child(m)
        self.assertIs(m, d.maps[0])
        for key in 'abc':                                  # check contains
            self.assertIn(key, d)
        for k, v in dict(a=1, B=20, C=30, z=100).items():  # check get
            self.assertEqual(d.get(k, 100), v)



class TestCounter(unittest.TestCase):

    def test_basics(self):
        c = Counter('abcaba')
        self.assertEqual(c, Counter({'a':3 , 'b': 2, 'c': 1}))
        self.assertEqual(c, Counter(a=3, b=2, c=1))
        self.assert_(isinstance(c, dict))
        self.assert_(isinstance(c, Mapping))
        self.assertTrue(issubclass(Counter, dict))
        self.assertTrue(issubclass(Counter, Mapping))
        self.assertEqual(len(c), 3)
        self.assertEqual(sum(c.values()), 6)
        self.assertEqual(sorted(c.values()), [1, 2, 3])
        self.assertEqual(sorted(c.keys()), ['a', 'b', 'c'])
        self.assertEqual(sorted(c), ['a', 'b', 'c'])
        self.assertEqual(sorted(c.items()),
                         [('a', 3), ('b', 2), ('c', 1)])
        self.assertEqual(c['b'], 2)
        self.assertEqual(c['z'], 0)
        self.assertEqual(c.__contains__('c'), True)
        self.assertEqual(c.__contains__('z'), False)
        self.assertEqual(c.get('b', 10), 2)
        self.assertEqual(c.get('z', 10), 10)
        self.assertEqual(c, dict(a=3, b=2, c=1))
        if not PY3:
            self.assertEqual(repr(c), "Counter({u'a': 3, u'b': 2, u'c': 1})")
        else:
            self.assertEqual(repr(c), "Counter({'a': 3, 'b': 2, 'c': 1})")
        self.assertEqual(c.most_common(), [('a', 3), ('b', 2), ('c', 1)])
        for i in range(5):
            self.assertEqual(c.most_common(i),
                             [('a', 3), ('b', 2), ('c', 1)][:i])
        self.assertEqual(''.join(sorted(c.elements())), 'aaabbc')
        c['a'] += 1         # increment an existing value
        c['b'] -= 2         # sub existing value to zero
        del c['c']          # remove an entry
        del c['c']          # make sure that del doesn't raise KeyError
        c['d'] -= 2         # sub from a missing value
        c['e'] = -5         # directly assign a missing value
        c['f'] += 4         # add to a missing value
        self.assertEqual(c, dict(a=4, b=0, d=-2, e=-5, f=4))
        self.assertEqual(''.join(sorted(c.elements())), 'aaaaffff')
        self.assertEqual(c.pop('f'), 4)
        self.assertNotIn('f', c)
        for i in range(3):
            elem, cnt = c.popitem()
            self.assertNotIn(elem, c)
        c.clear()
        self.assertEqual(c, {})
        self.assertEqual(repr(c), 'Counter()')
        self.assertRaises(NotImplementedError, Counter.fromkeys, 'abc')
        self.assertRaises(TypeError, hash, c)
        c.update(dict(a=5, b=3))
        c.update(c=1)
        c.update(Counter('a' * 50 + 'b' * 30))
        c.update()          # test case with no args
        c.__init__('a' * 500 + 'b' * 300)
        c.__init__('cdc')
        c.__init__()
        self.assertEqual(c, dict(a=555, b=333, c=3, d=1))
        self.assertEqual(c.setdefault('d', 5), 1)
        self.assertEqual(c['d'], 1)
        self.assertEqual(c.setdefault('e', 5), 5)
        self.assertEqual(c['e'], 5)

    def test_copying(self):
        # Check that counters are copyable, deepcopyable, picklable, and
        #have a repr/eval round-trip
        words = Counter('which witch had which witches wrist watch'.split())
        update_test = Counter()
        update_test.update(words)
        for i, dup in enumerate([
                    words.copy(),
                    copy.copy(words),
                    copy.deepcopy(words),
                    pickle.loads(pickle.dumps(words, 0)),
                    pickle.loads(pickle.dumps(words, 1)),
                    pickle.loads(pickle.dumps(words, 2)),
                    pickle.loads(pickle.dumps(words, -1)),
                    eval(repr(words)),
                    update_test,
                    Counter(words),
                    ]):
            msg = (i, dup, words)
            self.assertTrue(dup is not words)
            self.assertEqual(dup, words)
            self.assertEqual(len(dup), len(words))
            self.assertEqual(type(dup), type(words))

    def test_copy_subclass(self):
        class MyCounter(Counter):
            pass
        c = MyCounter('slartibartfast')
        d = c.copy()
        self.assertEqual(d, c)
        self.assertEqual(len(d), len(c))
        self.assertEqual(type(d), type(c))

    def test_conversions(self):
        # Convert to: set, list, dict
        s = 'she sells sea shells by the sea shore'
        self.assertEqual(sorted(Counter(s).elements()), sorted(s))
        self.assertEqual(sorted(Counter(s)), sorted(set(s)))
        self.assertEqual(dict(Counter(s)), dict(Counter(s).items()))
        self.assertEqual(set(Counter(s)), set(s))

    def test_invariant_for_the_in_operator(self):
        c = Counter(a=10, b=-2, c=0)
        for elem in c:
            self.assertTrue(elem in c)
            self.assertIn(elem, c)

    def test_multiset_operations(self):
        # Verify that adding a zero counter will strip zeros and negatives
        c = Counter(a=10, b=-2, c=0) + Counter()
        self.assertEqual(dict(c), dict(a=10))

        elements = 'abcd'
        for i in range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) for elem in elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) for elem in elements))
            q.update(h=1, i=-1, j=0)
            for counterop, numberop in [
                (Counter.__add__, lambda x, y: max(0, x+y)),
                (Counter.__sub__, lambda x, y: max(0, x-y)),
                (Counter.__or__, lambda x, y: max(0,x,y)),
                (Counter.__and__, lambda x, y: max(0, min(x,y))),
            ]:
                result = counterop(p, q)
                for x in elements:
                    self.assertEqual(numberop(p[x], q[x]), result[x],
                                     (counterop, x, p, q))
                # verify that results exclude non-positive counts
                self.assertTrue(x>0 for x in result.values())

        elements = 'abcdef'
        for i in range(100):
            # verify that random multisets with no repeats are exactly like sets
            p = Counter(dict((elem, randrange(0, 2)) for elem in elements))
            q = Counter(dict((elem, randrange(0, 2)) for elem in elements))
            for counterop, setop in [
                (Counter.__sub__, set.__sub__),
                (Counter.__or__, set.__or__),
                (Counter.__and__, set.__and__),
            ]:
                counter_result = counterop(p, q)
                set_result = setop(set(p.elements()), set(q.elements()))
                self.assertEqual(counter_result, dict.fromkeys(set_result, 1))

    def test_inplace_operations(self):
        elements = 'abcd'
        for i in range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2,4)) for elem in elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2,4)) for elem in elements))
            q.update(h=1, i=-1, j=0)
            for inplace_op, regular_op in [
                (Counter.__iadd__, Counter.__add__),
                (Counter.__isub__, Counter.__sub__),
                (Counter.__ior__, Counter.__or__),
                (Counter.__iand__, Counter.__and__),
            ]:
                c = p.copy()
                c_id = id(c)
                regular_result = regular_op(c, q)
                inplace_result = inplace_op(c, q)
                self.assertEqual(inplace_result, regular_result)
                self.assertEqual(id(inplace_result), c_id)

    def test_subtract(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50)
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        c.subtract(Counter(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50))
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter('aaabbcd')
        c.subtract('aaaabbcce')
        self.assertEqual(c, Counter(a=-1, b=0, c=-1, d=1, e=-1))

    def test_unary(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15,g=40)
        self.assertEqual(dict(+c), dict(c=5, d=10, e=15, g=40))
        self.assertEqual(dict(-c), dict(a=5))

    def test_repr_nonsortable(self):
        c = Counter(a=2, b=None)
        r = repr(c)
        self.assertIn("'a': 2", r)
        self.assertIn("'b': None", r)

    def test_helper_function(self):
        from xoutil.collections import _count_elements
        # two paths, one for real dicts and one for other mappings
        elems = list('abracadabra')

        d = dict()
        _count_elements(d, elems)
        self.assertEqual(d, {'a': 5, 'r': 2, 'b': 2, 'c': 1, 'd': 1})

        m = OrderedDict()
        _count_elements(m, elems)
        self.assertEqual(m,
             OrderedDict([('a', 5), ('b', 2), ('r', 2), ('c', 1), ('d', 1)]))


class TestOrderedDict(unittest.TestCase):

    def test_init(self):
        with self.assertRaises(TypeError):
            OrderedDict([('a', 1), ('b', 2)], None)                                 # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        self.assertEqual(sorted(OrderedDict(dict(pairs)).items()), pairs)           # dict input
        self.assertEqual(sorted(OrderedDict(**dict(pairs)).items()), pairs)         # kwds input
        self.assertEqual(list(OrderedDict(pairs).items()), pairs)                   # pairs input
        self.assertEqual(list(OrderedDict([('a', 1), ('b', 2), ('c', 9), ('d', 4)],
                                          c=3, e=5).items()), pairs)                # mixed input

        # make sure no positional args conflict with possible kwdargs
        self.assertEqual(inspect.getargspec(OrderedDict.__dict__['__init__']).args,
                         ['self'])

        # Make sure that direct calls to __init__ do not clear previous contents
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.__init__([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    def test_update(self):
        with self.assertRaises(TypeError):
            OrderedDict().update([('a', 1), ('b', 2)], None)                        # too many args
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)]
        od = OrderedDict()
        od.update(dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # dict input
        od = OrderedDict()
        od.update(**dict(pairs))
        self.assertEqual(sorted(od.items()), pairs)                                 # kwds input
        od = OrderedDict()
        od.update(pairs)
        self.assertEqual(list(od.items()), pairs)                                   # pairs input
        od = OrderedDict()
        od.update([('a', 1), ('b', 2), ('c', 9), ('d', 4)], c=3, e=5)
        self.assertEqual(list(od.items()), pairs)                                   # mixed input

        # Issue 9137: Named argument called 'other' or 'self'
        # shouldn't be treated specially.
        od = OrderedDict()
        od.update(self=23)
        self.assertEqual(list(od.items()), [('self', 23)])
        od = OrderedDict()
        od.update(other={})
        self.assertEqual(list(od.items()), [('other', {})])
        od = OrderedDict()
        od.update(red=5, blue=6, other=7, self=8)
        self.assertEqual(sorted(list(od.items())),
                         [('blue', 6), ('other', 7), ('red', 5), ('self', 8)])

        # Make sure that direct calls to update do not clear previous contents
        # add that updates items are not moved to the end
        d = OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 44), ('e', 55)])
        d.update([('e', 5), ('f', 6)], g=7, d=4)
        self.assertEqual(list(d.items()),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)])

    def test_abc(self):
        self.assert_(isinstance(OrderedDict(), MutableMapping))
        self.assertTrue(issubclass(OrderedDict, MutableMapping))

    def test_clear(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    def test_delitem(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        del od['a']
        self.assertNotIn('a', od)
        with self.assertRaises(KeyError):
            del od['a']
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    def test_setitem(self):
        od = OrderedDict([('d', 1), ('b', 2), ('c', 3), ('a', 4), ('e', 5)])
        od['c'] = 10           # existing element
        od['f'] = 20           # new element
        self.assertEqual(list(od.items()),
                         [('d', 1), ('b', 2), ('c', 10), ('a', 4), ('e', 5), ('f', 20)])

    def test_iterators(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(list(od), [t[0] for t in pairs])
        self.assertEqual(list(od.keys()), [t[0] for t in pairs])
        self.assertEqual(list(od.values()), [t[1] for t in pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)),
                         [t[0] for t in reversed(pairs)])

    def test_popitem(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        while pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        with self.assertRaises(KeyError):
            od.popitem()
        self.assertEqual(len(od), 0)

    def test_pop(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        shuffle(pairs)
        while pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        with self.assertRaises(KeyError):
            od.pop('xyz')
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

        # make sure pop still works when __missing__ is defined
        class Missing(OrderedDict):
            def __missing__(self, key):
                return 0
        m = Missing(a=1)
        self.assertEqual(m.pop('b', 5), 5)
        self.assertEqual(m.pop('a', 6), 1)
        self.assertEqual(m.pop('a', 6), 6)
        with self.assertRaises(KeyError):
            m.pop('a')

    def test_equality(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od1 = OrderedDict(pairs)
        od2 = OrderedDict(pairs)
        self.assertEqual(od1, od2)          # same order implies equality
        pairs = pairs[2:] + pairs[:2]
        od2 = OrderedDict(pairs)
        self.assertNotEqual(od1, od2)       # different order implies inequality
        # comparison to regular dict is not order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, OrderedDict(pairs[:-1]))

    def test_copying(self):
        # Check that ordered dicts are copyable, deepcopyable, picklable,
        # and have a repr/eval round-trip
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        update_test = OrderedDict()
        update_test.update(od)
        for i, dup in enumerate([
                    od.copy(),
                    copy.copy(od),
                    copy.deepcopy(od),
                    pickle.loads(pickle.dumps(od, 0)),
                    pickle.loads(pickle.dumps(od, 1)),
                    pickle.loads(pickle.dumps(od, 2)),
                    pickle.loads(pickle.dumps(od, -1)),
                    eval(repr(od)),
                    update_test,
                    OrderedDict(od),
                    ]):
            self.assertTrue(dup is not od)
            self.assertEqual(dup, od)
            self.assertEqual(list(dup.items()), list(od.items()))
            self.assertEqual(len(dup), len(od))
            self.assertEqual(type(dup), type(od))

    def test_yaml_linkage(self):
        # Verify that __reduce__ is setup in a way that supports PyYAML's dump() feature.
        # In yaml, lists are native but tuples are not.
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        # yaml.dump(od) -->
        # '!!python/object/apply:__main__.OrderedDict\n- - [a, 1]\n  - [b, 2]\n'
        self.assertTrue(all(type(pair)==list for pair in od.__reduce__()[1]))

    def test_reduce_not_too_fat(self):
        import sys
        # do not save instance dictionary if not needed
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        od = OrderedDict(pairs)
        if sys.version_info >= (3, 4):
            self.assertIsNone(od.__reduce__()[2])
        else:
            self.assertEqual(len(od.__reduce__()), 2)
        od.x = 10
        if sys.version_info >= (3, 4):
            self.assertIsNotNone(od.__reduce__()[2])
        else:
            self.assertEqual(len(od.__reduce__()), 3)

    def test_repr(self):
        od = OrderedDict([('c', 1), ('b', 2), ('a', 3)])
        if not PY3:
            self.assertEqual(
                repr(od),
                "OrderedDict([(u'c', 1), (u'b', 2), (u'a', 3)])")
        else:
            self.assertEqual(
                repr(od),
                "OrderedDict([('c', 1), ('b', 2), ('a', 3)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(OrderedDict()), "OrderedDict()")

    def test_repr_recursive(self):
        # See issue #9826
        od = OrderedDict.fromkeys('abc')
        od['x'] = od
        if not PY3:
            self.assertEqual(
                repr(od),
                "OrderedDict([(u'a', None), (u'b', None), (u'c', None), (u'x', ...)])")
        else:
            self.assertEqual(
                repr(od),
                "OrderedDict([('a', None), ('b', None), ('c', None), ('x', ...)])")

    def test_setdefault(self):
        pairs = [('c', 1), ('b', 2), ('a', 3), ('d', 4), ('e', 5), ('f', 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault('a', 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault('x', 10), 10)
        # make sure 'x' is added to the end
        self.assertEqual(list(od.items())[-1], ('x', 10))

        # make sure setdefault still works when __missing__ is defined
        class Missing(OrderedDict):
            def __missing__(self, key):
                return 0
        self.assertEqual(Missing().setdefault(5, 9), 9)

    def test_reinsert(self):
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a is now later than b.
        od = OrderedDict()
        od['a'] = 1
        od['b'] = 2
        del od['a']
        od['a'] = 1
        self.assertEqual(list(od.items()), [('b', 2), ('a', 1)])

    def test_move_to_end(self):
        od = OrderedDict.fromkeys('abcde')
        self.assertEqual(list(od), list('abcde'))
        od.move_to_end('c')
        self.assertEqual(list(od), list('abdec'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('c', 0)
        self.assertEqual(list(od), list('cabde'))
        od.move_to_end('e')
        self.assertEqual(list(od), list('cabde'))
        with self.assertRaises(KeyError):
            od.move_to_end('x')

    @unittest.skipIf('PyPy' in sys.version, 'sys.getsizeof not supported')
    def test_sizeof(self):
        # Wimpy test: Just verify the reported size is larger than a regular dict
        d = dict(a=1)
        od = OrderedDict(**d)
        self.assertGreater(sys.getsizeof(od), sys.getsizeof(d))

    def test_override_update(self):
        # Verify that subclasses can override update() without breaking __init__()
        class MyOD(OrderedDict):
            def update(self, *args, **kwds):
                raise Exception()
        items = [('a', 1), ('c', 3), ('b', 2)]
        self.assertEqual(list(MyOD(items).items()), items)


def test_abcs():
    from xoutil.collections import Container
    from xoutil.collections import Iterable
    from xoutil.collections import Iterator
    from xoutil.collections import Sized
    from xoutil.collections import Callable
    from xoutil.collections import Sequence
    from xoutil.collections import MutableSequence
    from xoutil.collections import Set
    from xoutil.collections import MutableSet
    from xoutil.collections import Mapping
    from xoutil.collections import MutableMapping
    from xoutil.collections import MappingView
    from xoutil.collections import ItemsView
    from xoutil.collections import KeysView
    from xoutil.collections import ValuesView


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
