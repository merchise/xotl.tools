- Remove deprecated `!xoutil.objects.metaclass`:class:, use
  `xoutil.eight.meta.metaclass`:func: instead.

- Several modules are migrated to `xoutil.future`:mod:\ :

  - `~xoutil.future.types`:mod:.

  - `~xoutil.future.collections`:mod:.

  - `~xoutil.future.datetime`:mod:.

  - `~xoutil.future.functools`:mod:.

  - `~xoutil.future.inspect`:mod:.

  - `~xoutil.future.codecs`:mod:.

  - `~xoutil.future.json`:mod:.

  - `~xoutil.future.threading`:mod:.

  - `~xoutil.future.subprocess`:mod:.

  - `~xoutil.future.pprint`:mod:.

  - `~xoutil.future.textwrap`:mod:.

- Create ``__small__`` protocol for small string representations, see
  `xoutil.string.small`:func: for more information.

- Added function `xoutil.deprecation.import_deprecated`:func:,
  `~xoutil.deprecation.inject_deprecated`:func: can be deprecated now.

- Added function `xoutil.deprecation.deprecate_linked`:func: to deprecate full
  modules imported from a linked version.  The main example are all
  sub-modules of `xoutil.future`:mod:.

- The module ``xoutil.future.string`` was completelly removed in favor of:

  - `xoutil.future.codecs`:mod:\ : Moved here functions
    `~xoutil.future.codecs.force_encoding`,
    `~xoutil.future.codecs.safe_decode`, and
    `~xoutil.future.codecs.safe_encode`.

  - `xoutil.eight.string`:mod:\ : Technical string handling.  In this module:

    - `~xoutil.eight.string.force`:func:\ : Replaces old ``safe_str``, and
      ``force_str`` versions.

    - `~xoutil.eight.string.safe_join`:func:\ : Replaces old version in
      ``future`` module.  This function is useless, it's equivalent to::

        force(vale).join(force(item) for item in iterator)

    - `~xoutil.eight.string.force_ascii`:func:\ : Replaces old
      ``normalize_ascii``.   This function is safe and the result will be of
      standard ``str`` type containing only equivalent ASCII characters from
      the argument.

  - `xoutil.eight.text`:mod:\ : Text handling, strings can be part of
    internationalization processes.  In this module:

    - `~xoutil.eight.text.force`:func:\ : Replaces old ``safe_str``, and
      ``force_str`` versions, but always returning the text type.

    - `~xoutil.eight.text.safe_join`:func:\ : Replaces old version in
      ``future`` module, but in this case always return the text type.  This
      function is useless, it's equivalent to::

        force(vale).join(force(item) for item in iterator)

  - ``capitalize_word`` function was completely removed, use instead standard
    method ``word.capitalize()``.

  - Functions ``capitalize``, ``normalize_name``, ``normalize_title``,
    ``normalize_str``, ``parse_boolean``, ``parse_url_int`` were completely
    removed, nobody was using them.

  - ``normalize_unicode`` was completely removed, nobody was using it and it's
    equivalent to `xoutil.eight.text.force`:func:.

  - ``hyphen_name`` was moved to `xoutil.cli.tools`:mod:.  It was only used in
    this package.

  - ``strfnumber`` was moved as an internal function of
    'xoutil.future.datetime':mod: module.


  - Function ``normalize_slug`` was deprecated as it, new version is
    `~xoutil.string.slugify`:func:\ .

- Module `xoutil.params`:mod: was recovered and integrated with several
  dispare other modules to do the same thing.

  - Added function `~xoutil.params.issue_9137`:func: -- Helper to fix issue
    9137 (self ambiguity).

  - Added function `~xoutil.params.check_count`:func: -- Checker for positional
    arguments actual count against constrains.

  - Added function `~xoutil.params.check_default`:func: -- Default value
    getter when passed as a last excess positional argument.

  - Added function `~xoutil.params.single`:func: -- Return true only when a
    unique argument is given.

  - Added function `~xoutil.params.keywords_only`:func: -- Decorator to make a
    function to accepts its keywords arguments as keywords-only.

  - Added function `~xoutil.params.pop_keyword_arg`:func: -- Tool to get a
    value from keyword arguments using several possible names.

  - Added class `~xoutil.params.ParamManager`:class: -- Parameter manager in a
    "smart" way.

  - Added class `~xoutil.params.ParamScheme`:class: -- Parameter scheme
    definition for a manager.

  - Added class `~xoutil.params.ParamSchemeRow`:class: -- Parameter scheme
    complement.
