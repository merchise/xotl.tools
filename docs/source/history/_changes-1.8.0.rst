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

  .. note:: All modules remain importable from its future-less version,
     however, deprecated.

- Add function `xoutil.deprecation.import_deprecated`:func:,
  `~xoutil.deprecation.inject_deprecated`:func: can be deprecated now.

- Add function `xoutil.deprecation.deprecate_linked`:func: to deprecate full
  modules imported from a linked version.  The main example are all
  sub-modules of `xoutil.future`:mod:.

- Add function `xoutil.deprecation.deprecate_module`:func: to deprecate full
  modules when imported.

- Remove the module ``xoutil.string`` in favor of:

  - `xoutil.future.codecs`:mod:\ : Moved here functions
    `~xoutil.future.codecs.force_encoding`:func:,
    `~xoutil.future.codecs.safe_decode`:func:, and
    `~xoutil.future.codecs.safe_encode`:func:.

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
    removed.

  - ``normalize_unicode`` was completely removed, it's now replaced by
    `xoutil.eight.text.force`:func:.

  - ``hyphen_name`` was moved to `xoutil.cli.tools`:mod:.

  - ``strfnumber`` was moved as an internal function of
    'xoutil.future.datetime':mod: module.

  - Function ``normalize_slug`` is now deprecated.  You should use now
    `~xoutil.string.slugify`:func:\ .

- Create ``__small__`` protocol for small string representations, see
  `xoutil.string.small`:func: for more information.

- Remove ``xoutil.connote`` that was introduced provisionally in 1.7.1.

- Module `xoutil.params`:mod: was introduced provisionally in 1.7.1, but now
  has been fully recovered.

  - Add function `~xoutil.params.issue_9137`:func: -- Helper to fix issue 9137
    (self ambiguity).

  - Add function `~xoutil.params.check_count`:func: -- Checker for positional
    arguments actual count against constrains.

  - Add function `~xoutil.params.check_default`:func: -- Default value getter
    when passed as a last excess positional argument.

  - Add function `~xoutil.params.single`:func: -- Return true only when a
    unique argument is given.

  - Add function `~xoutil.params.keywords_only`:func: -- Decorator to make a
    function to accepts its keywords arguments as keywords-only.

  - Add function `~xoutil.params.pop_keyword_arg`:func: -- Tool to get a value
    from keyword arguments using several possible names.

  - Add class `~xoutil.params.ParamManager`:class: -- Parameter manager in a
    "smart" way.

  - Add class `~xoutil.params.ParamScheme`:class: -- Parameter scheme
    definition for a manager.

  - Add class `~xoutil.params.ParamSchemeRow`:class: -- Parameter scheme
    complement.

  - Remove ``xoutil.params.ParamConformer``.

- Module `xoutil.values`:mod: was recovered adding several new features (old
  name ``xoutil.cl`` was deprecated).

- Add **experimental** module `xoutil.fp`:mod: for Functional Programming
  stuffs.

- Add **experimental** module `xoutil.tasking`:mod:.

- Remove deprecated module ``xoutil.data``.  Add
  `xoutil.objects.adapt_exception`:func:.

- Remove deprecated `xoutil.dim.meta.Signature.isunit`:meth:.
