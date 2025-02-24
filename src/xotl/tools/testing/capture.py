#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import contextlib
import io


@contextlib.contextmanager
def captured_stdout():
    r"""Capture the output of ``sys.stdout``.

    Example:

    .. doctest::

       >>> with captured_stdout() as stdout:
       ...    print("hello")

       >>> stdout.getvalue() == 'hello\n'
       True

    .. versionadded:: 3.1.1

    """
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        yield f


@contextlib.contextmanager
def captured_stderr():
    r"""Capture the output of ``sys.stderr``.

    Example:

    .. doctest::

       >>> import sys
       >>> with captured_stderr() as stderr:
       ...    print("hello", file=sys.stderr)

       >>> stderr.getvalue() == 'hello\n'
       True

    .. versionadded:: 3.1.1

    """
    f = io.StringIO()
    with contextlib.redirect_stderr(f):
        yield f
