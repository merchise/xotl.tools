#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

import pytest


def test_regression_Command_repr():
    from xotl.tools.cli import Command

    class MyCommand(Command):
        def run(self):
            pass

    class Hidden(object):
        def run(self):
            pass

    Command.register(Hidden)

    cmd = MyCommand()
    assert repr(cmd) != ""
    registry = Command.registry
    assert registry.get("my-command")
    assert registry.get("hidden")


def test_can_actually_run_the_help():
    from xotl.tools.cli.app import main

    with pytest.raises(SystemExit):
        main(default="help")
