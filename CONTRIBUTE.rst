===========================
How to contribute to xoutil
===========================

Testing
=======

Running tests
-------------

`xoutil` uses `pytest` and `tox` for tests. We have a bundled version of pytest
in the ``runtests.py`` scripts so for running tests in your environment you
don't really have to install `pytest` and/or `tox`.

Given you have installed `xoutil` as development user-local package with::

    $ python setup.py develop --user

You may run the tests with::

    $ python runtests.py

Use the ``-h`` to show the `pytest` command line options.

If you have `tox` installed, then should have also Python 2.7, Python 3.2 and
PyPy interpreters installed and in your path to run the tests with
`tox`. Having done so, you may run the tests with::


    $ tox

This will run the tests suite in those three environments.


Writing tests
-------------

Testing was not introduced in `xoutil` until late in the project life. So there
are many modules that lack a proper test suite.

To ease the task of writing tests, we chose `pytest`.

We use both normal tests ("à la pytest") and doctest. The purpose of doctests
is testing the documentation instead of testing the code, which is the purpose
of the former.

Most of our normal tests are currently simple functions with the "test_" prefix
and are located in the ``tests/`` directory.

Many functions that lacks are, though, tested by our use in other
projects. However, it won't hurt if we write them.


Documentation
=============

Since `xoutil` is collection of very disparate stuff, the documentation is
hardly narrative but is contained in the docstrings of every "exported"
element, except perhaps for module-level documentation in some cases. In these
later cases, a more narrative text is placed in the ``.rst`` file that
documents the module.


Versioning and deprecation
==========================

`xoutil` uses three version components.

The first number refers to language compatibility: `xoutil` 1.x series are
devoted to keeping compatible versions of the code for both Python 2.7 and
Python 3.2+. The jump to 2.x version series will made when `xoutil` won't
support Python 2.7 any longer.

The second number is library major version indicator. This indicates, that some
deprecated stuff are finally removed and/or new functionality is provided.

The third number is minor release number. Devoted to indicate mostly fixes to
existing functionality. Though many times, some functions are merged and the
old ones get a deprecation warning.

Occasionally, a fourth component is added to a release. This usually means a
packaging problem, or bug in the documentation.
