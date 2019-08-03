#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import unittest


class TestCLisp(unittest.TestCase):
    def test_basic_coercers(self):
        from xotl.tools.values import (
            identity_coerce,
            void_coerce,
            coercer,
            vouch,
            t,
            int_coerce,
            float_coerce,
            create_int_range_coerce,
            istype,
            typecast,
            iterable,
            mapping,
            create_unique_member_coerce,
            nil,
        )

        d = {"1": 2, 3.0: "4", 5.0 + 0j: 7.3 + 0j, 1: "2"}
        s = {1, "2", 3.0, "1"}
        l = [1, "2", 3.0, "1", "x10"]
        number_types = (int, float, complex)
        mc = mapping(int_coerce, float_coerce)
        uint_coerce = create_unique_member_coerce(int_coerce, d)
        mcu = mapping(uint_coerce, float_coerce)
        ic = iterable(int_coerce)
        age_coerce = create_int_range_coerce(0, 100)
        text_coerce = coercer(str)
        isnumber = istype(number_types)
        numbercast = typecast(number_types)
        # TODO: don't use isinstance
        self.assertEqual(
            all(
                isinstance(c, coercer)
                for c in (
                    mc,
                    mcu,
                    uint_coerce,
                    ic,
                    age_coerce,
                    text_coerce,
                    identity_coerce,
                    void_coerce,
                    int_coerce,
                    float_coerce,
                )
            ),
            True,
        )
        self.assertEqual(mc(dict(d)), {1: 2.0, 3: 4.0, 5: 7.3})
        self.assertIs(mcu(d), nil)
        self.assertEqual(mcu.scope, ({"1": 2}, uint_coerce))
        self.assertEqual(ic(s), {1, 2, 3})
        self.assertIs(ic(l), nil)
        self.assertIs(ic.scope, l[-1])
        self.assertEqual(l, [1, 2, 3, 1, "x10"])
        self.assertIs(age_coerce(80), 80)
        self.assertFalse(t(age_coerce(120)))
        self.assertIs(vouch(age_coerce, 80), 80)
        with self.assertRaises(TypeError):
            vouch(age_coerce, 120)
        self.assertIs(isnumber(5), 5)
        self.assertIs(isnumber(5.1), 5.1)
        with self.assertRaises(TypeError):
            vouch(isnumber, "5.1")
        self.assertIs(numbercast(5), 5)
        self.assertIs(numbercast(5.1), 5.1)
        self.assertEqual(numbercast("5.1"), 5.1)
        self.assertIs(numbercast.scope, float)

    def test_compound_coercers(self):
        from xotl.tools.values import (
            coercer,
            compose,
            some,
            combo,
            iterable,
            typecast,
            int_coerce,
            float_coerce,
            nil,
        )

        isstr = coercer(str)
        strcast = typecast(str)
        toint = compose(isstr, int_coerce)
        isint = some(isstr, int_coerce)
        hyphenjoin = coercer(lambda arg: "-".join(arg))
        intjoin = compose(iterable(strcast), hyphenjoin)
        cb = combo(strcast, int_coerce, float_coerce)
        self.assertEqual(toint("10"), 10)
        self.assertIs(toint(10), nil)
        self.assertEqual(toint.scope, (10, isstr))
        self.assertEqual(isint("10"), "10")
        self.assertEqual(isint.scope, isstr)
        self.assertEqual(isint(10), 10)
        self.assertEqual(isint.scope, int_coerce)
        self.assertEqual(intjoin(2 * i + 1 for i in range(5)), "1-3-5-7-9")
        self.assertEqual(cb([1, "2.0", 3, 4]), ["1", 2, 3.0])
