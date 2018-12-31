`xotl.tools.future.functools`:mod: - Higher-order functions and callable objects
================================================================================

.. module:: xotl.tools.future.functools

This module extends the standard library's `functools`:mod:.  You may use it
as a drop-in replacement in many cases.

Avoid importing ``*`` from this module since could be different in Python 2.7
and Python 3.3.

We added the following features.

.. autofunction:: power(*funcs, times)

.. autoclass:: lwraps(f, n, *, name=None, doc=None, wrapped=None)

.. autofunction:: curry

We have backported several Python 3.3 features but maybe not all.

.. function:: update_wrapper(wrapper, wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES)

   Update a wrapper function to look like the wrapped function.  The optional
   arguments are tuples to specify which attributes of the original function
   are assigned directly to the matching attributes on the wrapper function
   and which attributes of the wrapper function are updated with the
   corresponding attributes from the original function.  The default values
   for these arguments are the module level constants `WRAPPER_ASSIGNMENTS`
   (which assigns to the wrapper function's `__name__`, `__module__`,
   `__annotations__` and `__doc__`, the documentation string) and
   `WRAPPER_UPDATES` (which updates the wrapper function's `__dict__`, i.e.
   the instance dictionary).

   To allow access to the original function for introspection and other
   purposes (e.g.  bypassing a caching decorator such as `lru_cache`:func:),
   this function automatically adds a `__wrapped__` attribute to the wrapper
   that refers to the original function.

   The main intended use for this function is in decorator functions which
   wrap the decorated function and return the wrapper.  If the wrapper
   function is not updated, the metadata of the returned function will reflect
   the wrapper definition rather than the original function definition, which
   is typically less than helpful.

   `update_wrapper`:func: may be used with callables other than functions.
   Any attributes named in assigned or updated that are missing from the
   object being wrapped are ignored (i.e.  this function will not attempt to
   set them on the wrapper function).  AttributeError is still raised if the
   wrapper function itself is missing any attributes named in updated.
..
   Local Variables:
   ispell-dictionary: "en"
   End:
