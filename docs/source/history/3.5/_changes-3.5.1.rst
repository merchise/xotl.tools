.. rubric:: Python support

- Added support for Python 3.15.  The support matrix is now Python 3.10, 3.11, 3.12, 3.13, 3.14 and
  3.15.

.. rubric:: Changes

- Distributed now with ``uv_build``.  The generated module ``xotl.tools._version`` is no longer
  generated.  Since this was never a public API, we won't consider this a breaking change.
