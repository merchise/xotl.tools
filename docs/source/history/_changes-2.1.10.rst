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

- Add official support for Python 3.9.  We now our test
