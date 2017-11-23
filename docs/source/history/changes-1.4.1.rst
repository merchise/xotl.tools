- Deprecations and introductions:

  - Importing `xoutil.Unset`:data: and `xoutil.Ignored`:data: from
    `xoutil.types`:mod: now issues a warning.

  - New style for declaring portable metaclasses in
    `xoutil.objects.metaclass`:func:, so
    `xoutil.decorator.compat.metaclass`:func: is now deprecated.

  - Adds the module `xoutil.pprint`:mod: and function
    `xoutil.pprint.ppformat`:func:.

  - Adds the first version of package `xoutil.cli`:mod:.

  - Adds the `filter` parameter to functions `xoutil.objects.xdir`:func: and
    `xoutil.objects.fdir`:func: and deprecates `attr_filter` and
    `value_filter`.

  - Adds functions `xoutil.objects.attrclass`:func:,
    `xoutil.objects.fulldir`:func:.

  - Adds function `xoutil.iterators.continuously_slides`:func:.

  - Adds package `xoutil.threading`:mod:.

  - Adds package ``xoutil.html`` module and begins the port of
    ``xoutil.html.parser`` from Python 3.3 to xoutil, so that a common
    implementation for both Python 2.7 and Python 3.3 is available.

- Bug fixes:

  - Fixes some errors with `classical <!xoutil.aop.classical>`:mod: AOP weaving
    of functions in modules that where `customized
    <xoutil.modules.customize>`:func:.

  - Fixes bugs with `xoutil.modules`:mod:: makes
    `xoutil.modules.modulemethod`:func: to customize the module, and improves
    performance.
