- Remove deprecated ``xoutil.objects.metaclass``, use
  ``xoutil.eight.meta.metaclass`` instead.

- Several modules are migrated to ``xoutil.future``\ :

  .. hlist::
     :columns: 3

     - ``xoutil.future.types``.
     - ``xoutil.future.collections``.
     - ``xoutil.future.datetime``.
     - ``xoutil.future.functools``.
     - ``xoutil.future.inspect``.
     - ``xoutil.future.codecs``.
     - ``xoutil.future.json``.
     - ``xoutil.future.threading``.
     - ``xoutil.future.subprocess``.
     - ``xoutil.future.pprint``.
     - ``xoutil.future.textwrap``.

  .. note:: All modules remain importable from its future-less version,
     however, deprecated.

- Add function ``xoutil.deprecation.import_deprecated``,
  ``xoutil.deprecation.inject_deprecated`` can be deprecated now.

- Add function ``xoutil.deprecation.deprecate_linked`` to deprecate full
  modules imported from a linked version.  The main example are all
  sub-modules of ``xoutil.future``.

- Add function ``xoutil.deprecation.deprecate_module`` to deprecate full
  modules when imported.

- The module ``xoutil.string`` suffered a major reorganization due to
  ambiguity use of Strings in Python.

- Create ``__crop__`` protocol for small string representations, see
  ``xoutil.clipping.crop`` for more information.

  Because ``xoutil.clipping`` module is still **experimental**, definitive
  names of operator and main function must be validated before it could be
  considered definitive.  Proposals are: "crop", "small", "short", "compact",
  "abbr".

- Remove ``xoutil.connote`` that was introduced provisionally in 1.7.1.

- Module ``xoutil.params`` was introduced provisionally in 1.7.1, but now
  has been fully recovered.

  - Add function ``xoutil.params.issue_9137`` -- Helper to fix issue 9137
    (self ambiguity).

  - Add function ``xoutil.params.check_count`` -- Checker for positional
    arguments actual count against constrains.

  - Add function ``xoutil.params.check_default`` -- Default value getter
    when passed as a last excess positional argument.

  - Add function ``xoutil.params.single`` -- Return true only when a
    unique argument is given.

  - Add function ``xoutil.params.keywords_only`` -- Decorator to make a
    function to accepts its keywords arguments as keywords-only.

  - Add function ``xoutil.params.pop_keyword_arg`` -- Tool to get a value
    from keyword arguments using several possible names.

  - Add class ``xoutil.params.ParamManager`` -- Parameter manager in a
    "smart" way.

  - Add class ``xoutil.params.ParamScheme`` -- Parameter scheme
    definition for a manager.

  - Add class ``xoutil.params.ParamSchemeRow`` -- Parameter scheme
    complement.

  - Remove ``xoutil.params.ParamConformer``.

- Module ``xoutil.values`` was recovered adding several new features (old
  name ``xoutil.cl`` was deprecated).

- Add **experimental** module ``xoutil.fp`` for Functional Programming
  stuffs.

- Add **experimental** module ``xoutil.tasking``.

- Add ``xoutil.symbols``.  It replaces ``xoutil.logical`` that was
  introduced in 1.7.0, but never documented.

- Remove deprecated module ``xoutil.data``.  Add
  ``xoutil.objects.adapt_exception``.

- Remove deprecated ``xoutil.dim.meta.Signature.isunit``.
