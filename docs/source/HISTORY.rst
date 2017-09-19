Changelog
=========

1.7 series
----------

2017-09-19.  1.7.8
~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.8.rst


2017-09-07. 1.7.7
~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.7.rst


2017-09-05.  Release 1.7.6
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.6.rst


2017-09-05.  Release 1.7.5
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.5.rst


2017-04-06. Release 1.7.4
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.4.rst


2017-02-23. Release 1.7.3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.3.rst


2017-02-07. Release 1.7.2
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.2.rst


2015-12-17. Release 1.7.1
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.1.rst

.. warning:: Due to lack of time, we have decided to release this version
   without proper releases of 1.7.0 and 1.6.11.


.. _release-1.7.0:

Unreleased. Release 1.7.0
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.7.0.rst


1.6 series
----------


Unreleased. Release 1.6.11
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.11.rst


2015-04-15. Release 1.6.10
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.10.rst


2015-04-03.  Release 1.6.9
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.9.rst


2015-01-26. Release 1.6.8
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.8.rst


2014-12-17. Release 1.6.7
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.7.rst


2014-11-26. Release 1.6.6
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.6.rst


2014-10-13. Release 1.6.5
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.5.rst


2014-09-13. Release 1.6.4
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.4.rst

2014-08-05. Release 1.6.3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.3.rst


2014-08-04. Release 1.6.2
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.2.rst


2014-07-18. Release 1.6.1
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.1.rst


2014-06-02. Release 1.6.0
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.6.0.rst


1.5 series
----------

2014-05-29. Release 1.5.6
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.6.rst


2014-05-13. Release 1.5.5
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.5.rst

2014-04-08. Release 1.5.4
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.4.rst


2014-04-01. Release 1.5.3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.3.rst

2014-03-03. Release 1.5.2
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.2.rst


2014-02-14. Release 1.5.1
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.1.rst


2014-01-24. Release 1.5.0
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/_changes-1.5.0.rst


1.4 series
----------

.. include:: history/changes-1.4.2.rst
.. include:: history/changes-1.4.1.rst

2013-04-26. Release 1.4.0
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/changes-1.4.0.rst


1.3 series
----------

.. include:: history/changes-1.3.0.rst

1.2 series
----------

2013-04-03. Release 1.2.3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/changes-1.2.3.rst


2013-03-25. Release 1.2.2
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/changes-1.2.2.rst


2013-02-14. Release 1.2.1
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/changes-1.2.1.rst


2013-01-04. Release 1.2.0
~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: history/changes-1.2.0.rst


1.1 series
----------

2012-11-01. Release 1.1.4
~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces :func:`xoutil.compat.iteritems_`, :func:`xoutil.compat.iterkeys_`
  and :func:`xoutil.compat.itervalues_`.

- :mod:`execution context <xoutil.context>` are now aware of `zope.interface`
  interfaces; so that you may ask for a context name implementing a given
  interface, instead of the name itself.

- Improves xoutil.formatter documentation.

- Several fixes to :mod:`xoutil.aop.classical`. It has sudden backwards
  incompatible changes.

- `before` and `after` methods may use the `*args, **kwargs` idiom to get the
  passed arguments of the weaved method.

- Several minor fixes: Invalid warning about Unset not in xoutil.types

2012-08-22. Release 1.1.3
~~~~~~~~~~~~~~~~~~~~~~~~~

- Adds function :func:`xoutil.fs.rmdirs` that removes empty dirs.

- Adds functions :func:`xoutil.string.safe_join`,
  :func:`xoutil.string.safe_encode`, :func:`xoutil.string.safe_decode`,
  and :func:`xoutil.string.safe_strip`; and the class
  :class:`xoutil.string.SafeFormatter`.

- Adds function :func:`xoutil.cpystack.iter_frames`.

2012-07-11. Release 1.1.2
~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixes all copyrights notices and chooses the PSF License for Python 3.2.3
  as the license model for xoutil releases.

- All releases from now on will be publicly available at github_.

.. _github: https://github.com/merchise-autrement/xoutil/

.. TODO: Migrate some stuffs from "/merchise-autrement/" by "/merchise/"

2012-07-06. Release 1.1.1
~~~~~~~~~~~~~~~~~~~~~~~~~

- Improves deprecation warnings by pointing to the real calling filename
- Removes all internal use of simple_memoize since it's deprecated. We now use
  :func:`~xoutil.functools.lru_cache`.

2012-07-03. Release 1.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~

- Created the whole documentation Sphinx directory.

- Removed xoutil.future since it was not properly tested.

- Removed xoutil.annotate, since it's not portable across Python's VMs.

- Introduced module :mod:`xoutil.collections`

- Deprecated modules :mod:`xoutil.default_dict`, :mod:`xoutil.opendict` in
  favor of :mod:`xoutil.collections`.

- Backported :func:`xoutil.functools.lru_cache` from Python 3.2.

- Deprecated module :mod:`xoutil.memoize` in favor of
  :func:`xoutil.functools.lru_cache`.


1.0 series
----------

2012-06-15. Release 1.0.30
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces a new module :py:mod:`xoutil.proxy`.

- Starts working on the sphinx documentation so that we move to 1.1 release we
  a decent documentation.

2012-06-01. Release 1.0.29.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces `xoutil.iterators.slides` and `xoutil.aop.basic.contextualized`

2012-05-28. Release 1.0.28.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixes normalize path and other details
- Makes validate_attrs to work with mappings as well as objects
- Improves complementors to use classes as a special case of sources
- Simplifies importing of legacy modules
- PEP8

2012-05-22. Release 1.0.27.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Removes bugs that were not checked (tested) in the previous release.

2012-05-21. Release 1.0.26.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Changes in AOP classic. Now you have to rename after, before and around methods
  to _after, _before and _around.

  It is expected that the signature of those methods change in the future.

- Introducing a default argument for :func:`xoutil.objects.get_first_of`.

- Other minor additions in the code. Refactoring and the like.

2012-04-30. Release 1.0.25.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Extends the classical AOP approach to modules. Implements an extended version
  with hooks.

- 1.0.25.1: Makes classical/extended AOP more reliable to TypeError's in getattr.
  xoonko, may raise TypeError's for TranslatableFields.

2012-04-27. Release 1.0.24.

- Introduces a classical AOP implementation: xoutil.aop.classical.

2012-04-10. Release 1.0.23.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces decorators: xoutil.decorators.instantiate and xoutil.aop.complementor

2012-04-05. Release 1.0.22
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Allows annotation's expressions to use defined local variables.  Before this
  release the following code raised an error::

        >>> from xoutil.annotate import annotate
        >>> x1 = 1
        >>> @annotation('(a: x1)')
        ... def dummy():
        ...     pass
        Traceback (most recent call last):
           ...
        NameError: global name 'x1' is not defined

- Fixes decorators to allow args-less decorators


2012-04-03. Release 1.0.21
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Includes a new module :mod:`xoutil.annotate` that provides a way to place
  Python annotations in forward-compatible way.
