- Remove deprecated `!xoutil.objects.metaclass`:class:, use
  `xoutil.eight.meta.metaclass`:func: instead.

- Several modules are migrated to `xoutil.future`:mod:\ :

  .. hlist::
     :columns: 3

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

- The module `xoutil.string`:mod: suffered a major reorganization due to
  ambiguity use of Strings in Python.

- Create ``__crop__`` protocol for small string representations, see
  `xoutil.clipping.crop`:func: for more information.

  Because `~xoutil.clipping`:mod: module is still **experimental**, definitive
  names of operator and main function must be validated before it could be
  considered definitive.  Proposals are: "crop", "small", "short", "compact",
  "abbr".

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

  - Add function ``xoutil.params.keywords_only`` -- Decorator to make a
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

- Add `xoutil.symbols`:mod:.  It replaces `!xoutil.logical`:mod: that was
  introduced in 1.7.0, but never documented.

- Remove deprecated module ``xoutil.data``.  Add
  `xoutil.objects.adapt_exception`:func:.

- Remove deprecated `xoutil.dim.meta.Signature.isunit`:meth:.
