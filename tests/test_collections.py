#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import sys
import unittest

from random import shuffle
from xotl.tools.future.collections import defaultdict


class TestCollections(unittest.TestCase):
    def test_defaultdict(self):
        d = defaultdict(lambda key, _: "a")
        self.assertEqual("a", d["abc"])
        d["abc"] = 1
        self.assertEqual(1, d["abc"])

    def test_defaultdict_clone(self):
        d = defaultdict(lambda key, d: d["a"], {"a": "default"})
        self.assertEqual("default", d["abc"])

        d = defaultdict(lambda key, d: d[key])
        with self.assertRaises(KeyError):
            d["abc"]


def test_stacked_dict_with_newpop():
    """Test that stacked.pop has the same semantics has dict.pop."""
    from xotl.tools.future.collections import StackedDict

    sd = StackedDict(a="level-0", b=1)
    assert sd.pop("a") == "level-0"
    assert sd.pop("non", sd) is sd
    try:
        sd.pop("non")
    except KeyError:
        pass
    else:
        assert False, "Should have raised a KeyError"


def test_stacked_dict():
    from xotl.tools.future.collections import StackedDict

    sd = StackedDict(a="level-0")
    assert sd.peek() == dict(a="level-0")
    sd.push_level(a=1, b=2, c=10)
    assert sd.level == 1
    assert sd.peek() == dict(a=1, b=2, c=10)
    sd.push_level(b=4, c=5)
    assert sd.peek() == dict(b=4, c=5)
    assert sd.level == 2
    assert sd["b"] == 4
    assert sd["a"] == 1
    assert sd["c"] == 5
    assert len(sd) == 3
    del sd["c"]
    try:
        del sd["c"]
        assert False, "Should have raise KeyError"
    except KeyError:
        pass
    except:
        assert False, "Should have raise KeyError"
    assert sd.pop_level() == {"b": 4}
    assert sd["b"] == 2
    assert sd["a"] == 1
    assert len(sd) == 3
    sd.pop_level()
    assert sd["a"] == "level-0"
    try:
        sd.pop_level()
        assert False, "Level 0 cannot be poped. " "It should have raised a TypeError"
    except TypeError:
        pass
    except:
        assert False, "Level 0 cannot be poped. " "It should have raised a TypeError"


# Backported from Python 3.3.0 standard library
from xotl.tools.future.collections import ChainMap, Counter
from xotl.tools.future.collections import OrderedDict, RankedDict
from xotl.tools.future.collections import Mapping, MutableMapping
import copy
import pickle
from random import randrange


def _items(d):
    "For some reason in new PyPy 5.0.1 for Py 2.7.10, set order is not nice."
    from xotl.tools.versions import python_version

    res = d.items()
    if python_version.pypy and isinstance(res, list):
        res.sort()
    return res


class TestChainMap(unittest.TestCase):
    def test_basics(self):
        c = ChainMap()
        c["a"] = 1
        c["b"] = 2
        d = c.new_child()
        d["b"] = 20
        d["c"] = 30
        # check internal state
        self.assertEqual(d.maps, [{"b": 20, "c": 30}, {"a": 1, "b": 2}])
        # check items/iter/getitem
        self.assertEqual(_items(d), _items(dict(a=1, b=20, c=30)))
        # check len
        self.assertEqual(len(d), 3)
        # check contains
        for key in "abc":
            self.assertIn(key, d)
        # check get
        for k, v in dict(a=1, b=20, c=30, z=100).items():
            self.assertEqual(d.get(k, 100), v)

        # unmask a value
        del d["b"]
        # check internal state
        self.assertEqual(d.maps, [{"c": 30}, {"a": 1, "b": 2}])
        # check items/iter/getitem
        self.assertEqual(_items(d), _items(dict(a=1, b=2, c=30)))
        # check len
        self.assertEqual(len(d), 3)
        # check contains
        for key in "abc":
            self.assertIn(key, d)
        # check get
        for k, v in dict(a=1, b=2, c=30, z=100).items():
            self.assertEqual(d.get(k, 100), v)
        # check repr
        self.assertIn(
            repr(d),
            [
                type(d).__name__ + "({'c': 30}, {'a': 1, 'b': 2})",
                type(d).__name__ + "({'c': 30}, {'b': 2, 'a': 1})",
            ],
        )

        # check shallow copies
        for e in d.copy(), copy.copy(d):
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            self.assertIsNot(d.maps[0], e.maps[0])
            for m1, m2 in zip(d.maps[1:], e.maps[1:]):
                self.assertIs(m1, m2)

        # check deep copies
        for e in [pickle.loads(pickle.dumps(d)), copy.deepcopy(d), eval(repr(d))]:
            self.assertEqual(d, e)
            self.assertEqual(d.maps, e.maps)
            self.assertIsNot(d, e)
            for m1, m2 in zip(d.maps, e.maps):
                self.assertIsNot(m1, m2, e)

        f = d.new_child()
        f["b"] = 5
        self.assertEqual(f.maps, [{"b": 5}, {"c": 30}, {"a": 1, "b": 2}])
        # check parents
        self.assertEqual(f.parents.maps, [{"c": 30}, {"a": 1, "b": 2}])
        # find first in chain
        self.assertEqual(f["b"], 5)
        # look beyond maps[0]
        self.assertEqual(f.parents["b"], 2)

    def test_contructor(self):
        # no-args --> one new dict
        self.assertEqual(ChainMap().maps, [{}])
        # 1 arg --> list
        self.assertEqual(ChainMap({1: 2}).maps, [{1: 2}])

    def test_bool(self):
        self.assertFalse(ChainMap())
        self.assertFalse(ChainMap({}, {}))
        self.assertTrue(ChainMap({1: 2}, {}))
        self.assertTrue(ChainMap({}, {1: 2}))

    def test_missing(self):
        class DefaultChainMap(ChainMap):
            def __missing__(self, key):
                return 999

        d = DefaultChainMap(dict(a=1, b=2), dict(b=20, c=30))
        for k, v in dict(a=1, b=2, c=30, d=999).items():
            # check __getitem__ w/missing
            self.assertEqual(d[k], v)
        for k, v in dict(a=1, b=2, c=30, d=77).items():
            # check get() w/ missing
            self.assertEqual(d.get(k, 77), v)
        for k, v in dict(a=True, b=True, c=True, d=False).items():
            # check __contains__ w/missing
            self.assertEqual(k in d, v)
        self.assertEqual(d.pop("a", 1001), 1, d)
        # check pop() w/missing
        self.assertEqual(d.pop("a", 1002), 1002)
        # check popitem() w/missing
        self.assertEqual(d.popitem(), ("b", 2))
        with self.assertRaises(KeyError):
            d.popitem()

    def test_dict_coercion(self):
        d = ChainMap(dict(a=1, b=2), dict(b=20, c=30))
        self.assertEqual(dict(d), dict(a=1, b=2, c=30))
        self.assertEqual(dict(d.items()), dict(a=1, b=2, c=30))

    def test_new_child(self):
        "Tests for changes for issue #16613."
        c = ChainMap()
        c["a"] = 1
        c["b"] = 2
        m = {"b": 20, "c": 30}
        d = c.new_child(m)
        # check internal state
        self.assertEqual(d.maps, [{"b": 20, "c": 30}, {"a": 1, "b": 2}])
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
        c["a"] = 1
        c["b"] = 2
        m = lowerdict(b=20, c=30)
        d = c.new_child(m)
        self.assertIs(m, d.maps[0])
        # check contains
        for key in "abc":
            self.assertIn(key, d)
        # check get
        for k, v in dict(a=1, B=20, C=30, z=100).items():
            self.assertEqual(d.get(k, 100), v)


class TestCounter(unittest.TestCase):
    def test_basics(self):
        c = Counter("abcaba")
        self.assertEqual(c, Counter({"a": 3, "b": 2, "c": 1}))
        self.assertEqual(c, Counter(a=3, b=2, c=1))
        self.assertIsInstance(c, dict)
        self.assertIsInstance(c, Mapping)
        self.assertTrue(issubclass(Counter, dict))
        self.assertTrue(issubclass(Counter, Mapping))
        self.assertEqual(len(c), 3)
        self.assertEqual(sum(c.values()), 6)
        self.assertEqual(sorted(c.values()), [1, 2, 3])
        self.assertEqual(sorted(c.keys()), ["a", "b", "c"])
        self.assertEqual(sorted(c), ["a", "b", "c"])
        self.assertEqual(sorted(c.items()), [("a", 3), ("b", 2), ("c", 1)])
        self.assertEqual(c["b"], 2)
        self.assertEqual(c["z"], 0)
        self.assertEqual(c.__contains__("c"), True)
        self.assertEqual(c.__contains__("z"), False)
        self.assertEqual(c.get("b", 10), 2)
        self.assertEqual(c.get("z", 10), 10)
        self.assertEqual(c, dict(a=3, b=2, c=1))
        self.assertEqual(repr(c), "Counter({'a': 3, 'b': 2, 'c': 1})")
        self.assertEqual(c.most_common(), [("a", 3), ("b", 2), ("c", 1)])
        for i in range(5):
            self.assertEqual(c.most_common(i), [("a", 3), ("b", 2), ("c", 1)][:i])
        self.assertEqual("".join(sorted(c.elements())), "aaabbc")
        c["a"] += 1  # increment an existing value
        c["b"] -= 2  # sub existing value to zero
        del c["c"]  # remove an entry
        del c["c"]  # make sure that del doesn't raise KeyError
        c["d"] -= 2  # sub from a missing value
        c["e"] = -5  # directly assign a missing value
        c["f"] += 4  # add to a missing value
        self.assertEqual(c, dict(a=4, b=0, d=-2, e=-5, f=4))
        self.assertEqual("".join(sorted(c.elements())), "aaaaffff")
        self.assertEqual(c.pop("f"), 4)
        self.assertNotIn("f", c)
        for i in range(3):
            elem, cnt = c.popitem()
            self.assertNotIn(elem, c)
        c.clear()
        self.assertEqual(c, {})
        self.assertEqual(repr(c), "Counter()")
        self.assertRaises(NotImplementedError, Counter.fromkeys, "abc")
        self.assertRaises(TypeError, hash, c)
        c.update(dict(a=5, b=3))
        c.update(c=1)
        c.update(Counter("a" * 50 + "b" * 30))
        c.update()  # test case with no args
        c.__init__("a" * 500 + "b" * 300)
        c.__init__("cdc")
        c.__init__()
        self.assertEqual(c, dict(a=555, b=333, c=3, d=1))
        self.assertEqual(c.setdefault("d", 5), 1)
        self.assertEqual(c["d"], 1)
        self.assertEqual(c.setdefault("e", 5), 5)
        self.assertEqual(c["e"], 5)

    def test_copying(self):
        # Check that counters are copyable, deepcopyable, picklable, and
        # have a repr/eval round-trip
        words = Counter("which witch had which witches wrist watch".split())
        update_test = Counter()
        update_test.update(words)
        for i, dup in enumerate(
            [
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
            ]
        ):
            # TODO: Not used ``msg = (i, dup, words)``
            self.assertTrue(dup is not words)
            self.assertEqual(dup, words)
            self.assertEqual(len(dup), len(words))
            self.assertEqual(type(dup), type(words))

    def test_copy_subclass(self):
        class MyCounter(Counter):
            pass

        c = MyCounter("slartibartfast")
        d = c.copy()
        self.assertEqual(d, c)
        self.assertEqual(len(d), len(c))
        self.assertEqual(type(d), type(c))

    def test_conversions(self):
        # Convert to: set, list, dict
        s = "she sells sea shells by the sea shore"
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

        elements = "abcd"
        for i in range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2, 4)) for elem in elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2, 4)) for elem in elements))
            q.update(h=1, i=-1, j=0)
            for counterop, numberop in [
                (Counter.__add__, lambda x, y: max(0, x + y)),
                (Counter.__sub__, lambda x, y: max(0, x - y)),
                (Counter.__or__, lambda x, y: max(0, x, y)),
                (Counter.__and__, lambda x, y: max(0, min(x, y))),
            ]:
                result = counterop(p, q)
                for x in elements:
                    self.assertEqual(
                        numberop(p[x], q[x]), result[x], (counterop, x, p, q)
                    )
                # verify that results exclude non-positive counts
                self.assertTrue(x > 0 for x in result.values())

        elements = "abcdef"
        for i in range(100):
            # verify that random multisets with no repeats are exactly like
            # sets
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
        elements = "abcd"
        for i in range(1000):
            # test random pairs of multisets
            p = Counter(dict((elem, randrange(-2, 4)) for elem in elements))
            p.update(e=1, f=-1, g=0)
            q = Counter(dict((elem, randrange(-2, 4)) for elem in elements))
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
        c = Counter(a=-5, b=0, c=5, d=10, e=15, g=40)
        c.subtract(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50)
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter(a=-5, b=0, c=5, d=10, e=15, g=40)
        c.subtract(Counter(a=1, b=2, c=-3, d=10, e=20, f=30, h=-50))
        self.assertEqual(c, Counter(a=-6, b=-2, c=8, d=0, e=-5, f=-30, g=40, h=50))
        c = Counter("aaabbcd")
        c.subtract("aaaabbcce")
        self.assertEqual(c, Counter(a=-1, b=0, c=-1, d=1, e=-1))

    def test_unary(self):
        c = Counter(a=-5, b=0, c=5, d=10, e=15, g=40)
        self.assertEqual(dict(+c), dict(c=5, d=10, e=15, g=40))
        self.assertEqual(dict(-c), dict(a=5))

    def test_repr_nonsortable(self):
        c = Counter(a=2, b=None)
        r = repr(c)
        self.assertIn("'a': 2", r)
        self.assertIn("'b': None", r)

    def test_helper_function(self):
        from xotl.tools.future.collections import _count_elements

        # two paths, one for real dicts and one for other mappings
        elems = list("abracadabra")

        d = dict()
        _count_elements(d, elems)
        self.assertEqual(d, {"a": 5, "r": 2, "b": 2, "c": 1, "d": 1})

        m = OrderedDict()
        _count_elements(m, elems)
        self.assertEqual(
            m, OrderedDict([("a", 5), ("b", 2), ("r", 2), ("c", 1), ("d", 1)])
        )


class TestOrderedDict(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            # too many args
            OrderedDict([("a", 1), ("b", 2)], None)
        pairs = [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5)]
        # dict input
        self.assertEqual(sorted(OrderedDict(dict(pairs)).items()), pairs)
        # kwds input
        self.assertEqual(sorted(OrderedDict(**dict(pairs)).items()), pairs)
        # pairs input
        self.assertEqual(list(OrderedDict(pairs).items()), pairs)
        # mixed input
        self.assertEqual(
            list(
                OrderedDict([("a", 1), ("b", 2), ("c", 9), ("d", 4)], c=3, e=5).items()
            ),
            pairs,
        )

        # Make sure that direct calls to __init__ do not clear previous
        # contents
        d = OrderedDict([("a", 1), ("b", 2), ("c", 3), ("d", 44), ("e", 55)])
        d.__init__([("e", 5), ("f", 6)], g=7, d=4)
        self.assertEqual(
            list(d.items()),
            [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5), ("f", 6), ("g", 7)],
        )

    def test_update(self):
        with self.assertRaises(TypeError):
            # too many args
            OrderedDict().update([("a", 1), ("b", 2)], None)
        pairs = [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5)]
        od = OrderedDict()
        od.update(dict(pairs))
        # dict input
        self.assertEqual(sorted(od.items()), pairs)
        od = OrderedDict()
        od.update(**dict(pairs))
        # kwds input
        self.assertEqual(sorted(od.items()), pairs)
        od = OrderedDict()
        od.update(pairs)
        # pairs input
        self.assertEqual(list(od.items()), pairs)
        od = OrderedDict()
        od.update([("a", 1), ("b", 2), ("c", 9), ("d", 4)], c=3, e=5)
        # mixed input
        self.assertEqual(list(od.items()), pairs)

        # Issue 9137: Named argument called 'other' or 'self'
        # shouldn't be treated specially.
        od = OrderedDict()
        od.update(self=23)
        self.assertEqual(list(od.items()), [("self", 23)])
        od = OrderedDict()
        od.update(other={})
        self.assertEqual(list(od.items()), [("other", {})])
        od = OrderedDict()
        od.update(red=5, blue=6, other=7, self=8)
        self.assertEqual(
            sorted(list(od.items())),
            [("blue", 6), ("other", 7), ("red", 5), ("self", 8)],
        )

        # Make sure that direct calls to update do not clear previous contents
        # add that updates items are not moved to the end
        d = OrderedDict([("a", 1), ("b", 2), ("c", 3), ("d", 44), ("e", 55)])
        d.update([("e", 5), ("f", 6)], g=7, d=4)
        self.assertEqual(
            list(d.items()),
            [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5), ("f", 6), ("g", 7)],
        )

    def test_abc(self):
        self.assertIsInstance(OrderedDict(), MutableMapping)
        self.assertTrue(issubclass(OrderedDict, MutableMapping))

    def test_clear(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    def test_delitem(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = OrderedDict(pairs)
        del od["a"]
        self.assertNotIn("a", od)
        with self.assertRaises(KeyError):
            del od["a"]
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    def test_setitem(self):
        od = OrderedDict([("d", 1), ("b", 2), ("c", 3), ("a", 4), ("e", 5)])
        od["c"] = 10  # existing element
        od["f"] = 20  # new element
        self.assertEqual(
            list(od.items()),
            [("d", 1), ("b", 2), ("c", 10), ("a", 4), ("e", 5), ("f", 20)],
        )

    def test_iterators(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        self.assertEqual(list(od), [t[0] for t in pairs])
        self.assertEqual(list(od.keys()), [t[0] for t in pairs])
        self.assertEqual(list(od.values()), [t[1] for t in pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)), [t[0] for t in reversed(pairs)])

    def test_popitem(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        while pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        with self.assertRaises(KeyError):
            od.popitem()
        self.assertEqual(len(od), 0)

    def test_pop(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        shuffle(pairs)
        while pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        with self.assertRaises(KeyError):
            od.pop("xyz")
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

        # make sure pop still works when __missing__ is defined
        class Missing(OrderedDict):
            def __missing__(self, key):
                return 0

        m = Missing(a=1)
        self.assertEqual(m.pop("b", 5), 5)
        self.assertEqual(m.pop("a", 6), 1)
        self.assertEqual(m.pop("a", 6), 6)
        with self.assertRaises(KeyError):
            m.pop("a")

    def test_equality(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od1 = OrderedDict(pairs)
        od2 = OrderedDict(pairs)
        # same order implies equality
        self.assertEqual(od1, od2)
        pairs = pairs[2:] + pairs[:2]
        od2 = OrderedDict(pairs)
        # different order implies inequality
        self.assertNotEqual(od1, od2)
        # comparison to regular dict is not order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, OrderedDict(pairs[:-1]))

    def test_copying(self):
        # Check that ordered dicts are copyable, deepcopyable, picklable,
        # and have a repr/eval round-trip
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = OrderedDict(pairs)
        update_test = OrderedDict()
        update_test.update(od)
        for i, dup in enumerate(
            [
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
            ]
        ):
            self.assertTrue(dup is not od)
            self.assertEqual(dup, od)
            self.assertEqual(list(dup.items()), list(od.items()))
            self.assertEqual(len(dup), len(od))
            self.assertEqual(type(dup), type(od))

    def test_yaml_linkage(self):
        # Verify that __reduce__ is setup in a way that supports PyYAML's
        # dump() feature.
        # In yaml, lists are native but tuples are not.
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = OrderedDict(pairs)
        # yaml.dump(od) -->
        # '!!python/object/apply:__main__.OrderedDict\n- - [a, 1]\n  - [b, 2]\n'
        self.assertTrue(all(type(pair) == list for pair in od.__reduce__()[1]))

    def test_reduce_not_too_fat(self):
        import sys

        # do not save instance dictionary if not needed
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = OrderedDict(pairs)
        self.assertIsNone(od.__reduce__()[2])
        od.x = 10
        self.assertIsNotNone(od.__reduce__()[2])

    def test_repr(self):
        od = OrderedDict([("c", 1), ("b", 2), ("a", 3)])
        self.assertEqual(repr(od), "OrderedDict([('c', 1), ('b', 2), ('a', 3)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(OrderedDict()), "OrderedDict()")

    def test_repr_recursive(self):
        # See issue #9826
        od = OrderedDict.fromkeys("abc")
        od["x"] = od
        self.assertEqual(
            repr(od),
            ("OrderedDict([('a', None), ('b', None), " "('c', None), ('x', ...)])"),
        )

    def test_setdefault(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = OrderedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault("a", 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault("x", 10), 10)
        # make sure 'x' is added to the end
        self.assertEqual(list(od.items())[-1], ("x", 10))

        # make sure setdefault still works when __missing__ is defined
        class Missing(OrderedDict):
            def __missing__(self, key):
                return 0

        self.assertEqual(Missing().setdefault(5, 9), 9)

    def test_reinsert(self):
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a is now later than b.
        od = OrderedDict()
        od["a"] = 1
        od["b"] = 2
        del od["a"]
        od["a"] = 1
        self.assertEqual(list(od.items()), [("b", 2), ("a", 1)])

    def test_move_to_end(self):
        od = OrderedDict.fromkeys("abcde")
        self.assertEqual(list(od), list("abcde"))
        od.move_to_end("c")
        self.assertEqual(list(od), list("abdec"))
        od.move_to_end("c", 0)
        self.assertEqual(list(od), list("cabde"))
        od.move_to_end("c", 0)
        self.assertEqual(list(od), list("cabde"))
        od.move_to_end("e")
        self.assertEqual(list(od), list("cabde"))
        with self.assertRaises(KeyError):
            od.move_to_end("x")

    @unittest.skipIf("PyPy" in sys.version, "sys.getsizeof not supported")
    def test_sizeof(self):
        # Wimpy test: Just verify the reported size is larger than a regular
        # dict
        d = dict(a=1)
        od = OrderedDict(**d)
        self.assertGreater(sys.getsizeof(od), sys.getsizeof(d))

    def test_override_update(self):
        # Verify that subclasses can override update() without breaking
        # __init__()
        class MyOD(OrderedDict):
            def update(self, *args, **kwds):
                raise Exception()

        items = [("a", 1), ("c", 3), ("b", 2)]
        self.assertEqual(list(MyOD(items).items()), items)


class TestRankedDict(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            # too many args
            RankedDict([("a", 1), ("b", 2)], None)
        pairs = [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5)]
        # dict input
        self.assertEqual(sorted(RankedDict(dict(pairs)).items()), pairs)
        # kwds input
        self.assertEqual(sorted(RankedDict(**dict(pairs)).items()), pairs)
        # pairs input
        self.assertEqual(list(RankedDict(pairs).items()), pairs)
        # mixed input
        self.assertNotEqual(
            list(
                RankedDict([("a", 1), ("b", 2), ("c", 9), ("d", 4)], c=3, e=5).items()
            ),
            pairs,
        )

        # Make sure that direct calls to __init__ do not clear previous
        # contents
        d = RankedDict([("a", 1), ("b", 2), ("c", 3), ("d", 44), ("e", 55)])
        d.__init__([("f", 6), ("e", 5)], d=4)
        self.assertEqual(
            list(d.items()),
            [("a", 1), ("b", 2), ("c", 3), ("f", 6), ("e", 5), ("d", 4)],
        )

    def test_update(self):
        with self.assertRaises(TypeError):
            # too many args
            RankedDict().update([("a", 1), ("b", 2)], None)
        pairs = [("a", 1), ("b", 2), ("c", 3), ("d", 4), ("e", 5)]
        od = RankedDict()
        od.update(dict(pairs))
        # dict input
        self.assertEqual(sorted(od.items()), pairs)
        od = RankedDict()
        od.update(**dict(pairs))
        # kwds input
        self.assertEqual(sorted(od.items()), pairs)
        od = RankedDict()
        od.update(pairs)
        # pairs input
        self.assertEqual(list(od.items()), pairs)
        od = RankedDict()
        od.update([("a", 1), ("b", 2), ("c", 9), ("d", 4)], c=3, e=5)
        # mixed input
        self.assertNotEqual(list(od.items()), pairs)

        # Issue 9137: Named argument called 'other' or 'self'
        # shouldn't be treated specially.
        od = RankedDict()
        od.update(self=23)
        self.assertEqual(list(od.items()), [("self", 23)])
        od = RankedDict()
        od.update(other={})
        self.assertEqual(list(od.items()), [("other", {})])
        od = RankedDict()
        od.update(red=5, blue=6, other=7, self=8)
        self.assertEqual(
            sorted(list(od.items())),
            [("blue", 6), ("other", 7), ("red", 5), ("self", 8)],
        )

    def test_abc(self):
        self.assertIsInstance(RankedDict(), MutableMapping)
        self.assertTrue(issubclass(RankedDict, MutableMapping))

    def test_clear(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = RankedDict(pairs)
        self.assertEqual(len(od), len(pairs))
        od.clear()
        self.assertEqual(len(od), 0)

    def test_delitem(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = RankedDict(pairs)
        del od["a"]
        self.assertNotIn("a", od)
        with self.assertRaises(KeyError):
            del od["a"]
        self.assertEqual(list(od.items()), pairs[:2] + pairs[3:])

    def test_setitem(self):
        od = RankedDict([("d", 1), ("b", 2), ("c", 3), ("a", 4), ("e", 5)])
        od["c"] = 10  # existing element
        od["f"] = 20  # new element
        self.assertEqual(
            list(od.items()),
            [("d", 1), ("b", 2), ("a", 4), ("e", 5), ("c", 10), ("f", 20)],
        )

    def test_iterators(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = RankedDict(pairs)
        self.assertEqual(list(od), [t[0] for t in pairs])
        self.assertEqual(list(od.keys()), [t[0] for t in pairs])
        self.assertEqual(list(od.values()), [t[1] for t in pairs])
        self.assertEqual(list(od.items()), pairs)
        self.assertEqual(list(reversed(od)), [t[0] for t in reversed(pairs)])

    def test_popitem(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = RankedDict(pairs)
        while pairs:
            self.assertEqual(od.popitem(), pairs.pop())
        with self.assertRaises(KeyError):
            od.popitem()
        self.assertEqual(len(od), 0)

    def test_pop(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = RankedDict(pairs)
        shuffle(pairs)
        while pairs:
            k, v = pairs.pop()
            self.assertEqual(od.pop(k), v)
        with self.assertRaises(KeyError):
            od.pop("xyz")
        self.assertEqual(len(od), 0)
        self.assertEqual(od.pop(k, 12345), 12345)

        # make sure pop still works when __missing__ is defined
        class Missing(RankedDict):
            def __missing__(self, key):
                return 0

        m = Missing(a=1)
        self.assertEqual(m.pop("b", 5), 5)
        self.assertEqual(m.pop("a", 6), 1)
        self.assertEqual(m.pop("a", 6), 6)
        with self.assertRaises(KeyError):
            m.pop("a")

    def test_equality(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od1 = RankedDict(pairs)
        od2 = RankedDict(pairs)
        # same order implies equality
        self.assertEqual(od1, od2)
        pairs = pairs[2:] + pairs[:2]
        od2 = RankedDict(pairs)
        # different order implies inequality
        self.assertNotEqual(od1, od2)
        # comparison to regular dict is not order sensitive
        self.assertEqual(od1, dict(od2))
        self.assertEqual(dict(od2), od1)
        # different length implied inequality
        self.assertNotEqual(od1, RankedDict(pairs[:-1]))

    def test_copying(self):
        # Check that ranked dicts are copyable, deepcopyable, picklable,
        # and have a repr/eval round-trip
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = RankedDict(pairs)
        update_test = RankedDict()
        update_test.update(od)
        for i, dup in enumerate(
            [
                od.copy(),
                copy.copy(od),
                copy.deepcopy(od),
                pickle.loads(pickle.dumps(od, 0)),
                pickle.loads(pickle.dumps(od, 1)),
                pickle.loads(pickle.dumps(od, 2)),
                pickle.loads(pickle.dumps(od, -1)),
                eval(repr(od)),
                update_test,
                RankedDict(od),
            ]
        ):
            self.assertTrue(dup is not od)
            self.assertEqual(dup, od)
            self.assertEqual(list(dup.items()), list(od.items()))
            self.assertEqual(len(dup), len(od))
            self.assertEqual(type(dup), type(od))

    def test_yaml_linkage(self):
        # Verify that __reduce__ is setup in a way that supports PyYAML's
        # dump() feature.
        # In yaml, lists are native but tuples are not.
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        od = RankedDict(pairs)
        # yaml.dump(od) -->
        # '!!python/object/apply:__main__.RankedDict\n- - [a, 1]\n  - [b, 2]\n'
        self.assertTrue(all(type(pair) == list for pair in od.__reduce__()[1]))

    def test_repr(self):
        od = RankedDict([("c", 1), ("b", 2), ("a", 3)])
        self.assertEqual(repr(od), "RankedDict([('c', 1), ('b', 2), ('a', 3)])")
        self.assertEqual(eval(repr(od)), od)
        self.assertEqual(repr(RankedDict()), "RankedDict()")

    def test_repr_recursive(self):
        # See issue #9826
        od = RankedDict.fromkeys("abc")
        od["x"] = od
        self.assertEqual(
            repr(od),
            ("RankedDict([('a', None), ('b', None), " "('c', None), ('x', ...)])"),
        )

    def test_setdefault(self):
        pairs = [("c", 1), ("b", 2), ("a", 3), ("d", 4), ("e", 5), ("f", 6)]
        shuffle(pairs)
        od = RankedDict(pairs)
        pair_order = list(od.items())
        self.assertEqual(od.setdefault("a", 10), 3)
        # make sure order didn't change
        self.assertEqual(list(od.items()), pair_order)
        self.assertEqual(od.setdefault("x", 10), 10)
        # make sure 'x' is added to the end
        self.assertEqual(list(od.items())[-1], ("x", 10))

        # make sure setdefault still works when __missing__ is defined
        class Missing(RankedDict):
            def __missing__(self, key):
                return 0

        self.assertEqual(Missing().setdefault(5, 9), 9)

    def test_reinsert(self):
        # Given insert a, insert b, delete a, re-insert a,
        # verify that a is now later than b.
        od = RankedDict()
        od["a"] = 1
        od["b"] = 2
        del od["a"]
        od["a"] = 1
        self.assertEqual(list(od.items()), [("b", 2), ("a", 1)])

    def test_move_to_end(self):
        od = RankedDict.fromkeys("abcde")
        self.assertEqual(list(od), list("abcde"))
        od.move_to_end("c")
        self.assertEqual(list(od), list("abdec"))
        od.move_to_end("c", 0)
        self.assertEqual(list(od), list("cabde"))
        od.move_to_end("c", 0)
        self.assertEqual(list(od), list("cabde"))
        od.move_to_end("e")
        self.assertEqual(list(od), list("cabde"))
        with self.assertRaises(KeyError):
            od.move_to_end("x")

    @unittest.skipIf("PyPy" in sys.version, "sys.getsizeof not supported")
    def test_sizeof(self):
        # Wimpy test: Just verify the reported size is larger than a regular
        # dict
        d = dict(a=1)
        od = RankedDict(**d)
        self.assertGreater(sys.getsizeof(od), sys.getsizeof(d))


class TestPascalSet(unittest.TestCase):
    def test_consistency(self):
        from random import randint
        from xotl.tools.future.collections import PascalSet

        count = 5
        for test in range(count):
            size = randint(20, 60)
            ranges = (range(i, randint(i, i + 3)) for i in range(1, size))
            s1 = PascalSet(*ranges)
            ranges = (range(i, randint(i, i + 3)) for i in range(1, size))
            s2 = PascalSet(*ranges)
            ss1 = set(s1)
            ss2 = set(s2)
            self.assertEqual(s1, ss1)
            self.assertEqual(s1 - s2, ss1 - ss2)
            self.assertEqual(s2 - s1, ss2 - ss1)
            self.assertEqual(s1 & s2, ss1 & ss2)
            self.assertEqual(s2 & s1, ss2 & ss1)
            self.assertEqual(s1 | s2, ss1 | ss2)
            self.assertEqual(s2 | s1, ss2 | ss1)
            self.assertEqual(s1 ^ s2, ss1 ^ ss2)
            self.assertEqual(s2 ^ s1, ss2 ^ ss1)
            self.assertLess(s1 - s2, s1)
            self.assertLess(s1 - s2, ss1)
            self.assertLessEqual(s1 - s2, s1)
            self.assertLessEqual(s1 - s2, ss1)
            self.assertGreater(s1, s1 - s2)
            self.assertGreater(s1, ss1 - ss2)
            self.assertGreaterEqual(s1, s1 - s2)
            self.assertGreaterEqual(s1, ss1 - ss2)

    def test_syntax_sugar(self):
        from xotl.tools.future.collections import PascalSet

        s1 = PascalSet[1:4, 9, 15:18]
        s2 = PascalSet[3:18]
        self.assertEqual(str(s1), "{1..3, 9, 15..17}")
        self.assertEqual(str(s1 ^ s2), "{1, 2, 4..8, 10..14}")
        self.assertEqual(list(PascalSet[3:18]), list(range(3, 18)))

    def test_operators(self):
        from xotl.tools.future.collections import PascalSet

        g = lambda s: (i for i in s)
        s1 = PascalSet[1:4, 9, 15:18]
        r1 = range(1, 18)
        s2 = PascalSet(s1, 20)
        self.assertTrue(s1.issubset(s1))
        self.assertTrue(s1.issubset(set(s1)))
        self.assertTrue(s1.issubset(list(s1)))
        self.assertTrue(s1.issubset(g(s1)))
        self.assertTrue(s1.issubset(r1))
        self.assertTrue(s1.issubset(set(r1)))
        self.assertTrue(s1.issubset(list(r1)))
        self.assertTrue(s1.issubset(g(r1)))
        self.assertTrue(s2.issuperset(s2))
        self.assertTrue(s2.issuperset(s1))
        self.assertTrue(s2.issuperset(set(s1)))
        self.assertTrue(s2.issuperset(list(s1)))
        self.assertTrue(s2.issuperset(g(s1)))
        self.assertTrue(s1 <= set(s1))
        self.assertTrue(s1 < s2)
        self.assertTrue(s1 <= s2)
        self.assertTrue(s1 < set(s2))
        self.assertTrue(s1 <= set(s2))
        self.assertTrue(s1 < set(r1))
        self.assertTrue(s1 <= set(r1))
        self.assertTrue(s2 >= s2)
        self.assertTrue(s2 >= set(s2))
        self.assertTrue(s2 > s1)
        self.assertTrue(s2 > set(s1))
        self.assertTrue(s2 >= s1)
        self.assertTrue(s2 >= set(s1))

    def test_errors(self):
        """Test that stacked.pop has the same semantics has dict.pop."""
        from xotl.tools.future.collections import PascalSet

        s1 = PascalSet[1:4, 9, 15:18]
        s2 = PascalSet(s1, 20)
        self.assertLess(s1, s2)
        try:
            if s1 < list(s2):
                state = "less"
            else:
                state = "not-less"
        except TypeError:
            state = "TypeError"
        self.assertEqual(state, "TypeError")
        with self.assertRaises(TypeError):
            if s1 < set(s2):
                state = "ok"
            if s1 < list(s2):
                state = "safe-less"
            else:
                state = "safe-not-less"
        self.assertEqual(state, "ok")


class TestBitPascalSet(unittest.TestCase):
    def test_consistency(self):
        from random import randint
        from xotl.tools.future.collections import BitPascalSet

        count = 5
        for test in range(count):
            size = randint(20, 60)
            ranges = (range(i, randint(i, i + 3)) for i in range(1, size))
            s1 = BitPascalSet(*ranges)
            ranges = (range(i, randint(i, i + 3)) for i in range(1, size))
            s2 = BitPascalSet(*ranges)
            ss1 = set(s1)
            ss2 = set(s2)
            self.assertEqual(s1, ss1)
            self.assertEqual(s1 - s2, ss1 - ss2)
            self.assertEqual(s2 - s1, ss2 - ss1)
            self.assertEqual(s1 & s2, ss1 & ss2)
            self.assertEqual(s2 & s1, ss2 & ss1)
            self.assertEqual(s1 | s2, ss1 | ss2)
            self.assertEqual(s2 | s1, ss2 | ss1)
            self.assertEqual(s1 ^ s2, ss1 ^ ss2)
            self.assertEqual(s2 ^ s1, ss2 ^ ss1)
            self.assertLess(s1 - s2, s1)
            self.assertLess(s1 - s2, ss1)
            self.assertLessEqual(s1 - s2, s1)
            self.assertLessEqual(s1 - s2, ss1)
            self.assertGreater(s1, s1 - s2)
            self.assertGreater(s1, ss1 - ss2)
            self.assertGreaterEqual(s1, s1 - s2)
            self.assertGreaterEqual(s1, ss1 - ss2)

    def test_syntax_sugar(self):
        from xotl.tools.future.collections import BitPascalSet

        s1 = BitPascalSet[1:4, 9, 15:18]
        s2 = BitPascalSet[3:18]
        self.assertEqual(str(s1), "{1..3, 9, 15..17}")
        self.assertEqual(str(s1 ^ s2), "{1, 2, 4..8, 10..14}")
        self.assertEqual(list(BitPascalSet[3:18]), list(range(3, 18)))

    def test_operators(self):
        from xotl.tools.future.collections import BitPascalSet

        g = lambda s: (i for i in s)
        s1 = BitPascalSet[1:4, 9, 15:18]
        r1 = range(1, 18)
        s2 = BitPascalSet(s1, 20)
        self.assertTrue(s1.issubset(s1))
        self.assertTrue(s1.issubset(set(s1)))
        self.assertTrue(s1.issubset(list(s1)))
        self.assertTrue(s1.issubset(g(s1)))
        self.assertTrue(s1.issubset(r1))
        self.assertTrue(s1.issubset(set(r1)))
        self.assertTrue(s1.issubset(list(r1)))
        self.assertTrue(s1.issubset(g(r1)))
        self.assertTrue(s2.issuperset(s2))
        self.assertTrue(s2.issuperset(s1))
        self.assertTrue(s2.issuperset(set(s1)))
        self.assertTrue(s2.issuperset(list(s1)))
        self.assertTrue(s2.issuperset(g(s1)))
        self.assertTrue(s1 <= set(s1))
        self.assertTrue(s1 < s2)
        self.assertTrue(s1 <= s2)
        self.assertTrue(s1 < set(s2))
        self.assertTrue(s1 <= set(s2))
        self.assertTrue(s1 < set(r1))
        self.assertTrue(s1 <= set(r1))
        self.assertTrue(s2 >= s2)
        self.assertTrue(s2 >= set(s2))
        self.assertTrue(s2 > s1)
        self.assertTrue(s2 > set(s1))
        self.assertTrue(s2 >= s1)
        self.assertTrue(s2 >= set(s1))

    def test_errors(self):
        """Test that stacked.pop has the same semantics has dict.pop."""
        from xotl.tools.future.collections import BitPascalSet

        s1 = BitPascalSet[1:4, 9, 15:18]
        s2 = BitPascalSet(s1, 20)
        self.assertLess(s1, s2)
        try:
            if s1 < list(s2):
                state = "less"
            else:
                state = "not-less"
        except TypeError:
            state = "TypeError"
        self.assertEqual(state, "TypeError")
        with self.assertRaises(TypeError):
            if s1 < set(s2):
                state = "ok"
            if s1 < list(s2):
                state = "safe-less"
            else:
                state = "safe-not-less"
        self.assertEqual(state, "ok")


class TestCodeDict(unittest.TestCase):
    def test_formatter(self):
        from xotl.tools.future.collections import codedict

        cd = codedict(x=1, y=2, z=3.0)
        self.assertEqual(
            "{_[x + y]} is 3 --  {_[x + z]} is 4.0".format(_=cd),
            "3 is 3 --  4.0 is 4.0",
        )
        self.assertEqual(
            cd >> "{_[x + y]} is 3 --  {_[x + z]} is 4.0 -- {x} is 1",
            "3 is 3 --  4.0 is 4.0 -- 1 is 1",
        )
        self.assertEqual(
            "{_[x + y]} is 3 --  {_[x + z]} is 4.0 -- {x} is 1" << cd,
            "3 is 3 --  4.0 is 4.0 -- 1 is 1",
        )


def test_abcs():
    from xotl.tools.future.collections import Container  # noqa
    from xotl.tools.future.collections import Iterable  # noqa
    from xotl.tools.future.collections import Iterator  # noqa
    from xotl.tools.future.collections import Sized  # noqa
    from xotl.tools.future.collections import Callable  # noqa
    from xotl.tools.future.collections import Sequence  # noqa
    from xotl.tools.future.collections import MutableSequence  # noqa
    from xotl.tools.future.collections import Set  # noqa
    from xotl.tools.future.collections import MutableSet  # noqa
    from xotl.tools.future.collections import Mapping  # noqa
    from xotl.tools.future.collections import MutableMapping  # noqa
    from xotl.tools.future.collections import MappingView  # noqa
    from xotl.tools.future.collections import ItemsView  # noqa
    from xotl.tools.future.collections import KeysView  # noqa
    from xotl.tools.future.collections import ValuesView  # noqa


def test_opendict():
    try:
        from enum import Enum
    except ImportError:
        from enum34 import Enum

    from xotl.tools.future.collections import opendict

    class Foo:
        x = 1
        _y = 2

    foo = opendict.from_enum(Foo)
    assert dict(foo) == {"x": 1}

    class Bar(Enum):
        spam = "spam"

        def eat(self):
            return self.spam

    bar = opendict.from_enum(Bar)
    assert dict(bar) == {"spam": Bar.spam}


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main(verbosity=2)
