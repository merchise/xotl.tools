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
