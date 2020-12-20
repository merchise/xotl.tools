#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import os
import unittest
import tempfile
import shutil

# Makes sure our package is always importable
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                              '..', '..')))


class TestFs(unittest.TestCase):
    def setUp(self):
        # Makes all names predictable
        pjoin = os.path.join
        self.previous_dir = os.getcwd()
        self.base = base = tempfile.mkdtemp(prefix="xotl-tools-tests-")
        os.makedirs(pjoin(base, "A", "B", "C"))
        os.makedirs(pjoin(base, "A", "D", "E"))
        os.makedirs(pjoin(base, "A", "F"))
        self.files = files = []

        wexpected = self.walk_up_expected = pjoin(self.base, "A")
        sentinel = tempfile.mkstemp(prefix="X", dir=wexpected)
        self.sentinel = os.path.basename(sentinel[-1])
        files.append(sentinel)  # For testing `walk_up`
        files.append(tempfile.mkstemp(prefix="M", dir=pjoin(self.base, "A", "B")))
        files.append(tempfile.mkstemp(prefix="P", dir=pjoin(self.base, "A", "B")))
        wstart = self.walk_up_start = pjoin(self.base, "A", "B", "C")
        files.append(tempfile.mkstemp(prefix="z", dir=wstart))
        files.append(tempfile.mkstemp(suffix="ending", dir=pjoin(self.base, "A", "D")))
        files.append(tempfile.mkstemp(prefix="Z", dir=pjoin(self.base, "A", "F")))

    def test_iter_files_with_regex_pattern(self):
        from xotl.tools.fs import iter_files

        res = list(iter_files(self.base, "(?xi)/Z"))
        self.assertEqual(2, len(res))
        self.assertIn(self.files[-3][-1], res)
        self.assertIn(self.files[-1][-1], res)

    def test_iter_files_with_maxdepth(self):
        from xotl.tools.fs import iter_files

        res = list(iter_files(self.base, "(?xi)/Z", maxdepth=3))
        self.assertEqual(1, len(res))
        self.assertIn(self.files[-1][-1], res)
        res = list(iter_files(self.base, "(?xi)/Z", maxdepth=2))
        self.assertEqual(0, len(res))

    def test_walk_up(self):
        from xotl.tools.fs import walk_up

        expected, start = self.walk_up_expected, self.walk_up_start
        sentinel = self.sentinel
        self.assertEqual(expected, walk_up(start, sentinel))

    def test_ensure_filename(self):
        from xotl.tools.fs import ensure_filename

        filename = os.path.join(self.base, "en", "sure", "filename.txt")
        ensure_filename(filename)
        self.assertTrue(os.path.isfile(filename))

    def tearDown(self):
        shutil.rmtree(self.base)
        os.chdir(self.previous_dir)


if __name__ == "__main__":
    unittest.main()
