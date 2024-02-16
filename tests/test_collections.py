#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import copy
import pickle
import sys
import unittest
from collections.abc import MutableMapping
from random import shuffle

from xotl.tools.future.collections import DefaultDict, RankedDict, defaultdict


class TestDefaultDict(unittest.TestCase):
    def test_defaultdict(self):
        d = DefaultDict(lambda key, _: "a")
        self.assertEqual("a", d["abc"])
        d["abc"] = 1
        self.assertEqual(1, d["abc"])

    def test_defaultdict_clone(self):
        d = DefaultDict(lambda key, d: d["a"], {"a": "default"})
        self.assertEqual("default", d["abc"])

        d = DefaultDict(lambda key, d: d[key])
        with self.assertRaises(KeyError):
            d["abc"]


class TestDefaultDictAlias(unittest.TestCase):
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
    except Exception:
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
    except Exception:
        assert False, "Level 0 cannot be poped. " "It should have raised a TypeError"


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
            list(RankedDict([("a", 1), ("b", 2), ("c", 9), ("d", 4)], c=3, e=5).items()),
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
        for _i, dup in enumerate([
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
        ]):
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
        self.assertTrue(all(type(pair) is list for pair in od.__reduce__()[1]))

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


def test_opendict():
    from enum import Enum

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
