Changelog
=========

Reversed chronological order.

1.2 series
----------

2013-01-04. Release 1.2.0
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the first of the 1.2.0 series. It's been given a bump in the minor
version number because we've removed some deprecated functions and/or modules.

- Several enhancements to :mod:`xoutil.string` to make it work on Python 2.7
  and Python 3.2.

  Deprecates :func:`xoutil.string.normalize_to_str` in favor of the newly
  created :func:`xoutil.string.force_str`.

- Fixes in :mod:`xoutil.aop.extended`. Added parameters in
  :func:`xoutil.aop.classical.weave`.

- Introduces :func:`xoutil.iterators.first_n` and deprecates
  :func:`xoutil.iterators.first` and :func:`xoutil.iterators.get_first`.

- Removes the `zope.interface` awareness from :mod:`xoutil.context` since it
  contained a very hard to catch bug. Furthermore, this was included to help
  the implementation of `xotl.ql`, and it's no longer used there.

  This breaks version control policy since it was not deprecated beforehand,
  but we feel it's needed to avoid spreading this bug.

- Removed long-standing deprecated modules :mod:`xoutil.default_dict`,
  :mod:`xoutil.memoize` and :mod:`xoutil.opendict`.

- Fixes bug in :func:`xoutil.datetime.strfdelta`. It used to show things like
  '1h 62min'.

- Introduces :data:`xoutil.compat.class_type` that holds class types for Python
  2 or Python 3.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixes all copyrights notices and chooses the PSF License for Python 3.2.3
  as the license model for xoutil releases.

- All releases from now on will be publicly available at github_.

.. _github: https://github.com/merchise-autrement/xoutil/

2012-07-06. Release 1.1.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Improves deprecation warnings by pointing to the real calling filename
- Removes all internal use of simple_memoize since it's deprecated. We now use
  :func:`~xoutil.functools.lru_cache`.

2012-07-03. Release 1.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces a new module :py:mod:`xoutil.proxy`.

- Starts working on the sphinx documentation so that we move to 1.1 release we
  a decent documentation.

2012-06-01. Release 1.0.29.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces `xoutil.iterators.slides` and `xoutil.aop.basic.contextualized`

2012-05-28. Release 1.0.28.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixes normalize path and other details
- Makes validate_attrs to work with mappings as well as objects
- Improves complementors to use classes as a special case of sources
- Simplifies importing of legacy modules
- PEP8

2012-05-22. Release 1.0.27.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Removes bugs that were not checked (tested) in the previous release.

2012-05-21. Release 1.0.26.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Changes in AOP classic. Now you have to rename after, before and around methods
  to _after, _before and _around.

  It is expected that the signature of those methods change in the future.

- Introducing a default argument for :func:`xoutil.objects.get_first_of`.

- Other minor additions in the code. Refactoring and the like.

2012-04-30. Release 1.0.25.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Extends the classical AOP approach to modules. Implements an extended version
  with hooks.

- 1.0.25.1: Makes classical/extended AOP more reliable to TypeError's in getattr.
  xoonko, may raise TypeError's for TranslatableFields.

2012-04-27. Release 1.0.24.

- Introduces a classical AOP implementation: xoutil.aop.classical.

2012-04-10. Release 1.0.23.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Introduces decorators: xoutil.decorators.instantiate and xoutil.aop.complementor

2012-04-05. Release 1.0.22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Includes a new module :mod:`xoutil.annotate` that provides a way to place
  Python annotations in forward-compatible way.
