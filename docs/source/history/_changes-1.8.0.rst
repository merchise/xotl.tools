- Remove deprecated `!xoutil.objects.metaclass`:class:, use
  `xoutil.eight.meta.metaclass`:func: instead.

- Several modules are migrated to `xoutil.future`:mod:\ :

  - `~xoutil.future.types`:mod:.

  - `~xoutil.future.collections`:mod:.

  - `~xoutil.future.datetime`:mod:.

  - `~xoutil.future.functools`:mod:.

  - `~xoutil.future.inspect`:mod:.

  - `~xoutil.future.string`:mod:.

  - `~xoutil.future.codecs`:mod:.

  - `~xoutil.future.json`:mod:.

  - `~xoutil.future.threading`:mod:.

  - `~xoutil.future.subprocess`:mod:.

  - `~xoutil.future.pprint`:mod:.

  - `~xoutil.future.textwrap`:mod:.

- Create ``__small__`` protocol for small string representations, see
  `xoutil.future.string.small`:func: for more information.

- Migrations related with full deprecation of `xoutil.future.string`:mod:
  module:

  - ``force_encoding``, ``safe_decode``, ``safe_encode`` ->
    `xoutil.future.codecs`:mod:

  - ``safe_str`` -> `xoutil.eight.string`:mod: module, renaming it for
    ``force``.
