=========================================================
 :mod:`xoutil.params` -- Basic function argument manager
=========================================================

.. automodule:: xoutil.params
   :members: Coercer, TypeCheck, NoneOrTypeCheck, CheckAndCast, LogicalCheck,
             SafeCheck, MultiCheck

Because the nature of this tool, the term "parameter" will be used in this
documentation to reference those of the represented client function, and the
term "argument" for referencing those pertaining to `ParamManager`:class:
methods.

.. autoclass:: ParamManager
   :members: __init__, __call__, remainder

   When use this class as a callable, each identifier could be an integer or a
   string, respectively representing indexes in the positional and names in
   the keyword parameters.  Negative indexes are treated as in Python tuples
   or lists.

   Several identifiers must be unambiguous, or because some integers are
   already marked as consumed in previous calls or because an option coerce
   function validate only one position.  In the case of names, when one value
   is hit, all remainder names must be absent in the `kwargs` parameters.

   'coerce' option could be a callable, or a Python type (or a tuple of
   types).  When callable, must return a coerced valid value or `Invalid`;
   when type or types, `isinstance` standard function is used to check.


.. autoclass:: ParamScheme
   :members: get, defaults, __call__, __len__, __getitem__, __iter__

.. autoclass:: ParamSchemeRow
   :members: key, default, __call__

   This class generates callable instances receiving one `ParamManager`:class:
   instance as its single argument.
