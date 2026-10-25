`xotl.tools.cpystack`:mod: - Utilities to inspect the CPython's stack
=====================================================================

.. automodule:: xotl.tools.cpystack
   :members: getargvalues, error_info, printable_error_info, object_info_finder,
             object_finder, track_value, iter_stack

Migration guidance
==================

Use the standard-library `traceback`:mod: and `inspect`:mod: modules rather than introducing
another stack-inspection dependency.  They cover the underlying operations, but their return
formats and frame-selection conventions are not drop-in replacements.

- Replace ``getargvalues`` with `inspect.getargvalues`:func:.  The standard result keeps named,
  variadic positional, and variadic keyword arguments separate instead of flattening them into
  potentially colliding dictionary keys.

- Replace ``iter_stack`` with `traceback.walk_stack`:func:.  It yields ``(frame, lineno)`` pairs;
  pass the desired starting frame explicitly and use ``itertools.islice`` to limit traversal.
  Review which helper/caller frames should be included rather than assuming identical depths.

- For live traceback frames and selected local objects, use `traceback.walk_tb`:func: and explicit
  filtering.  For detached diagnostic summaries or formatting, prefer
  `traceback.TracebackException`:class:, `traceback.StackSummary`:class:, or
  `traceback.format_exception`:func: instead of ``error_info`` and ``printable_error_info``.

- Prefer explicit argument passing to ``object_info_finder``, ``object_finder``, and ``track_value``.
  If inspecting callers is genuinely necessary, implement a narrowly scoped search with ``inspect``
  or ``traceback`` and define its starting frame, matching rules, and ownership of frame references.

Capturing locals for ``TracebackException`` or ``StackSummary`` stores representations, not the
live objects returned by ``error_info``.  Python 3.12 stopped propagating exceptions raised by
those objects' ``repr`` methods during capture.  Python 3.14 changed ``walk_stack`` to capture the
stack state when called rather than when iteration begins.  Consult the `traceback documentation
<https://docs.python.org/3/library/traceback.html>`_ when supporting multiple Python versions.

Retaining live frames or local objects can keep large object graphs alive.  Local variables may
also contain credentials or other sensitive data; capture only what is needed and redact before
logging or publishing diagnostics.

Compatibility during deprecation
================================

This deprecation does not remove functions or constants or change their signatures.
No removal version or minimum retention period is promised.  Warnings are emitted inside the
functions, without wrapper frames that would alter stack depth.
``iter_stack`` emits its warning when iteration begins; importing the module does not warn.

Known defects are not repaired as part of this deprecation: ``object_finder`` attempts to call
its search result, unmatched ``error_info`` selectors can raise ``TypeError``, and ``track_value``
returns a context/name tuple rather than the dictionary described in its legacy docstring.
Review these behaviors when migrating rather than depending on them.
