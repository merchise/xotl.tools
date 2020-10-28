#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest
import pytest

# Test concurrent access to context by several greenlets.  Verify isolation in
# the greenlets.  We don't test isolation for threads cause that depends on
# python's thread locals and we *rely* on its correctness.
#
# Since xotl.tools.context inspects sys.modules to test for greenlet presence
# we need to import greenlets before importing context.
#
try:
    import greenlet
except ImportError:
    GREENLETS = False
else:
    GREENLETS = True

import sys

sys.modules.pop("xotl.tools.tasking", None)
sys.modules.pop("xotl.tools.context", None)
del sys

from xotl.tools.context import context


class TestContext(unittest.TestCase):
    def test_simple_contexts(self):
        with context("CONTEXT-1"):
            self.assertIsNot(None, context["CONTEXT-1"])
            with context("CONTEXT-1"):
                with context("context-2"):
                    self.assertIsNot(None, context["CONTEXT-1"])
                    self.assertIsNot(None, context["context-2"])
                self.assertEqual(False, bool(context["context-2"]))
            self.assertIsNot(None, context["CONTEXT-1"])
        self.assertEqual(False, bool(context["CONTEXT-1"]))

    def test_with_objects(self):
        CONTEXT1 = object()
        CONTEXT2 = object()
        with context(CONTEXT1):
            self.assertIsNot(None, context[CONTEXT1])
            with context(CONTEXT1):
                with context(CONTEXT2):
                    self.assertIsNot(None, context[CONTEXT1])
                    self.assertIsNot(None, context[CONTEXT2])
                self.assertEqual(False, bool(context[CONTEXT2]))
            self.assertIsNot(None, context[CONTEXT1])
        self.assertEqual(False, bool(context[CONTEXT1]))


def test_stacking_of_data_does_not_leak():
    c1 = "CONTEXT-1"
    with context(c1, a=1, b=1) as cc1:
        assert cc1["a"] == 1
        with context(c1, a=2, z="zzz") as cc2:
            assert cc2 is cc1
            assert cc2["a"] == 2
            assert cc2["b"] == 1  # Given by the upper enclosing level
            assert cc2["z"] == "zzz"

            # Let's change it for this level
            cc2["b"] = "jailed!"
            assert cc2["b"] == "jailed!"

        # But in the upper level both a and b stay the same
        assert cc1["a"] == 1
        assert cc1["b"] == 1
        assert set(cc1) == {"a", "b"}

    try:
        assert cc1["a"] == 1
        assert False
    except (IndexError, KeyError):
        pass


def test_data_is_an_opendict():
    c1 = object()
    with context(c1, a=1, b=1) as cc1:
        with context(c1, a=2) as cc2:
            assert cc2 is cc1
            assert cc2.a == 2
            assert cc2.b == 1  # Given by the upper enclosing level
            cc2.b = "jaile!d"
        assert cc1.a == 1
        assert cc1["b"] == 1


def test_reusing_raises():
    with context("a") as a:
        try:
            with a:
                pass
            assert False, "It should have raised a RuntimeError"
        except RuntimeError:
            pass
        except:  # noqa
            assert False, "It should have raised a RuntimeError"


def test_from_dicts():
    with context.from_dicts("A", dict(a=1), dict(a=2, b=1)) as c:
        assert c["a"] == 1
        assert c["b"] == 1
        with context.from_dicts("A", dict(a=2), dict(b=2)) as c:
            assert c["b"] == 1
            assert c["a"] == 2
        assert c["b"] == 1
        assert c["a"] == 1


def test_from_defaults():
    with context.from_defaults("A", a=1):
        with context.from_defaults("A", a=2, b=1) as c:
            assert c["a"] == 1
            assert c["b"] == 1
            with context("A", a=2) as c2:
                assert c2["a"] == 2
            # It recovers the value
            assert c["a"] == 1
        # and again
        assert c["a"] == 1


def test_recover_from_runtime_bug_33():
    try:
        with context("A") as c:
            with c:
                pass
    except RuntimeError:
        pass

    with context("A"):
        pass


def test_null_context_is_mapping():
    from xotl.tools.context import NullContext

    dict(**NullContext())


@pytest.mark.skipif(not GREENLETS, reason="greenlet is not installed")
def test_greenlet_contexts():
    import random
    from xotl.tools.symbols import Unset

    calls = 0
    switches = 0

    class GreenletProg:
        def __init__(self, arg):
            self.arg = arg

        def __call__(self):
            nonlocal calls
            nonlocal switches
            calls += 1
            switches += 1
            assert "GREEN CONTEXT" not in context
            with context("GREEN CONTEXT") as ctx:
                assert ctx.get("greenvar", Unset) is Unset
                ctx["greenvar"] = self.arg
                root.switch()
                switches += 1
                assert ctx["greenvar"] == self.arg
                # list() makes KeyViews pass in Python 3+
                assert list(ctx.keys()) == ["greenvar"]

    def loop(n):
        nonlocal calls
        nonlocal switches
        greenlets = [greenlet.greenlet(run=GreenletProg(i)) for i in range(n)]
        calls = 0
        switches = 0
        while greenlets:
            pos = random.randrange(0, len(greenlets))
            gl = greenlets[pos]
            gl.switch()
            # The gl has relinquished control, so if its dead removed from the
            # list, otherwise let it be for another round.
            if gl.dead:
                del greenlets[pos]
        assert calls == n, "There should be N calls to greenlets."
        assert switches == 2 * n, "There should be 2*N switches."

    def loop_determ(n):
        nonlocal calls
        nonlocal switches
        greenlets = [greenlet.greenlet(run=GreenletProg(i)) for i in range(n)]
        pos = 0
        calls = 0
        switches = 0
        while greenlets:
            gl = greenlets[pos]
            gl.switch()
            # The gl has relinquished control, so if its dead removed from the
            # list, otherwise let it be for another round.
            if gl.dead:
                del greenlets[pos]
            # In this case we ensure there will be several concurrent
            # greenlets
            pos = ((pos + 1) % len(greenlets)) if greenlets else 0
        assert calls == n, "There should be N calls to greenlets."
        assert switches == 2 * n, "There should be 2*N switches."

    root = greenlet.greenlet(run=loop)
    root.switch(10)

    root = greenlet.greenlet(run=loop_determ)
    root.switch(5)
