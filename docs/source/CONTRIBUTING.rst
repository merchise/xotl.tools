=====================================
 How to contribute to ``xotl.tools``
=====================================

Testing
=======

Running tests
-------------

Quick::

  pipenv install --dev
  tox


Writing tests
-------------

Testing was not introduced in ``xotl.tools`` until late in the project life.
So there are many modules that lack a proper test suite.

To ease the task of writing tests, we chose `pytest`.

We use both normal tests ("à la pytest") and doctest.  The purpose of doctests
is testing the documentation instead of testing the code, which is the purpose
of the former.

Most of our normal tests are currently simple functions with the "test" prefix
and are located in the ``tests/`` directory.

Many functions that lacks are, though, tested by our use in other projects.
However, it won't hurt if we write them.


Documentation
=============

Since ``xotl.tools`` is collection of very disparate stuff, the documentation
is hardly narrative but is contained in the docstrings of every "exported"
element, except perhaps for module-level documentation in some cases.  In
these later cases, a more narrative text is placed in the ``.rst`` file that
documents the module.


Versioning and deprecation
==========================

`xotl.tools` (previously ``xoutil``) uses three version components.

The first number refers to language compatibility: `xoutil` 1.x series are
devoted to keeping compatible versions of the code for both Python 2.7 and
Python 3.2+.  The jump to 2.x version series will made when `xoutil` won't
support Python 2.7 any longer.

From version 2.1.0, we renamed the package to ``xotl.tools`` but we keep
imports up to version 3.0, and distribution of ``xoutil`` up to version 2.2.0.

The second number is library major version indicator.  This indicates, that
some deprecated stuff are finally removed and/or new functionality is
provided.

The third number is minor release number.  Devoted to indicate mostly fixes to
existing functionality.  Though many times, some functions are merged and the
old ones get a deprecation warning.

Occasionally, a fourth component is added to a release.  This usually means a
packaging problem, or bug in the documentation.


Module layout and rules
=======================

Many modules in ``xotl.tools`` contains definitions used in ``xotl.tools``
itself.  Though we try to logically place every feature into a rightful,
logical module; sometimes this is not possible because it would lead to import
dependency cycles.

We are establishing several rules to keep our module layout and dependency
quite stable while, at the same time, allowing developers to use almost every
feature in xoutil.

We divide xoutil modules into 4 tiers:

#. Tier 0

   This tier groups the modules that **must not** depend from other modules
   besides the standard library.  These modules implement some features that
   are exported through other xoutil modules.  These module are never
   documented, but their re-exported features are documented elsewhere.

#. Tier 1

   In this tier we have:

   - `xotl.tools.decorator.meta`:mod:.  This is to allow the definition of
     decorators in other modules.

   - `xotl.tools.names`:mod:.  This is to allow the use of
     `xotl.tools.names.namelist`:class: for the ``__all__`` attribute of other
     modules.

   - `xotl.tools.deprecation`:mod:.  It **must not** depend on any other
     module.  Many modules in ``xotl.tools`` will use this module at import
     time to declare deprecated features.

#. Tier 2

   Modules in this tier should depend only on features defined in tiers 0 and 1
   modules, and that export features that could be imported at the module
   level.

   This tier only has the `xotl.tools.modules`:mod:.  Both
   `xotl.tools.modules.modulepropery`:func: and
   `xotl.tools.modules.modulemethod`:func: are meant be used at module level
   definitions, so they are likely to be imported at module level.

#. Tier 3

   The rest of the modules.

   In this tier, `xotl.tools.objects`:mod: is king.  But in order to allow the
   import of other modules the following pair of rules are placed:

  - At the module level only import from upper tiers.

  - Imports from tier 3 are allowed, but only inside the functions that use
    them.

  This entails that you can't define a function that must be a module level
  import, like a decorator for other functions.  For that reason, decorators
  are mostly placed in the `xotl.tools.decorator`:mod: module.


The tiers above are a "logical suggestion" of how xoutil modules are organized
and indicated how they might evolve.
