- Improve type hints for several modules.

  We run mypy 0.782 in a large project of ours that uses many modules of
  xotl.tools and we discovered no major roadblocks.  So we think this deserves
  its own release.

  The list of modules we deem are complete:

  - `xotl.tools.dim`:mod:
  - `xotl.tools.future.itertools`:mod:
  - `xotl.tools.fp.tools`:mod:
  - `xotl.tools.string`:mod:
  - `xotl.tools.future.objects`:mod:
  - `xotl.tools.future.datetime`:mod:
  - `xotl.tools.context`:mod:

  We've published several post-releases for 2.1.10 (2.1.10.post2,
  2.1.10.post3, ...).  Those releases don't introduce new functions or
  bug-fixes, only more and more support for type hints (those we've missed in
  the 2.1.10 release).

- Add official support for Python 3.9.  The list of Python versions we support
  is currently:

  - Python 3.6
  - Python 3.7
  - Python 3.8, and
  - Python 3.9.
