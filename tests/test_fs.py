#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.tests.test_fs
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on Feb 15, 2012

'Tests for xoutil.fs module'

import os
import sys
import unittest
import tempfile
import shutil

# Makes sure our package is always importable
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestFs(unittest.TestCase):
    def setUp(self):
        # Makes all names predictable
        pjoin = os.path.join
        self.previous_dir = os.getcwd()
        self.base = base = tempfile.mkdtemp(prefix='xoutiltests-')
        os.makedirs(pjoin(base, 'A', 'B', 'C'))
        os.makedirs(pjoin(base, 'A', 'D', 'E'))
        os.makedirs(pjoin(base, 'A', 'F'))
        self.files = files = []
        files.append(tempfile.mkstemp(prefix='X', dir=pjoin(self.base, 'A')))
        files.append(tempfile.mkstemp(prefix='M', dir=pjoin(self.base, 'A', 'B')))
        files.append(tempfile.mkstemp(prefix='P', dir=pjoin(self.base, 'A', 'B')))
        files.append(tempfile.mkstemp(prefix='z', dir=pjoin(self.base, 'A', 'B', 'C')))
        files.append(tempfile.mkstemp(suffix='ending', dir=pjoin(self.base, 'A', 'D')))
        files.append(tempfile.mkstemp(prefix='Z', dir=pjoin(self.base, 'A', 'F')))

    def test_iter_files_with_regex_pattern(self):
        from xoutil.fs import iter_files
        res = list(iter_files(self.base, '(?xi)/Z'))
        self.assertEquals(2, len(res))
        self.assertIn(self.files[-3][-1], res)
        self.assertIn(self.files[-1][-1], res)


    def test_iter_files_with_maxdepth(self):
        from xoutil.fs import iter_files
        res = list(iter_files(self.base, '(?xi)/Z', maxdepth=3))
        self.assertEquals(1, len(res))
        self.assertIn(self.files[-1][-1], res)

        res = list(iter_files(self.base, '(?xi)/Z', maxdepth=2))
        self.assertEquals(0, len(res))


    def tearDown(self):
        shutil.rmtree(self.base)
        os.chdir(self.previous_dir)

if __name__ == '__main__':
    unittest.main()
