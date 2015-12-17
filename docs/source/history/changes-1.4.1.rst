- Deprecations and introductions:

  - Importing :data:`xoutil.Unset` and :data:`xoutil.Ignored` from
    :mod:`xoutil.types` now issues a warning.

  - New style for declaring portable metaclasses in
    :func:`xoutil.objects.metaclass`, so
    :func:`xoutil.decorator.compat.metaclass` is now deprecated.

  - Adds the module :mod:`xoutil.pprint` and function
    :func:`xoutil.pprint.ppformat`.

  - Adds the first version of package :mod:`xoutil.cli`.

  - Adds the `filter` parameter to functions :func:`xoutil.objects.xdir` and
    :func:`xoutil.objects.fdir` and deprecates `attr_filter` and
    `value_filter`.

  - Adds functions :func:`xoutil.objects.attrclass`,
    :func:`xoutil.objects.fulldir`.

  - Adds function :func:`xoutil.iterators.continuously_slides`.

  - Adds package :mod:`xoutil.threading`.

  - Adds package :mod:`xoutil.html` and begins the port of
    :mod:`xoutil.html.parser` from Python 3.3 to xoutil, so that a common
    implementation for both Python 2.7 and Python 3.3 is available.


- Bug fixes:

  - Fixes some errors with :mod:`classical <!xoutil.aop.classical>` AOP weaving
    of functions in modules that where :func:`customized
    <xoutil.modules.customize>`.

  - Fixes bugs with :mod:`xoutil.modules`: makes
    :func:`xoutil.modules.modulemethod` to customize the module, and improves
    performance.
