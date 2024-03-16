#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import contextlib
import sys


@contextlib.contextmanager
def captured_output(stream_name):
    """Return a context manager used by captured_stdout/stdin/stderr
    that temporarily replaces the sys stream *stream_name* with a StringIO."""
    import io

    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, io.StringIO())
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)


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
    return captured_output("stdout")


def captured_stderr():
    r"""Capture the output of ``sys.stderr``.

    Example:

    .. doctest::

       >>> with captured_stderr() as stderr:
       ...    print("hello", file=sys.stderr)

       >>> stderr.getvalue() == 'hello\n'
       True

    .. versionadded:: 3.1.1

    """
    return captured_output("stderr")
