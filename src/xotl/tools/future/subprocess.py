#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
"""Extensions the `subprocess` module in the standard library."""

from subprocess import PIPE, Popen

__all__ = ["call_and_check_output"]


def call_and_check_output(*popenargs, **kwargs):
    """Combines `call` and `check_output`. Returns a tuple ``(returncode,
    output, err_output)``.

    """
    if "stdout" in kwargs:
        raise ValueError("stdout argument not allowed, it will be overridden.")
    kwargs["stdout"] = PIPE
    process = Popen(*popenargs, **kwargs)
    output, err = process.communicate()
    retcode = process.poll()
    return (retcode, output, err)
