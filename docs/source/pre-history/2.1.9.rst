- Add official support for Python 3.8 and drop support for Python 3.5.

  Even though our packages have been tested with Python 3.8 for a while.  This
  release marks the official support.

  Dropping support for Python 3.5 means we no longer going to test our changes
  in Python 3.5.

- Backport module `graphlib`:mod: from Python 3.9 in
  `!xotl.tools.future.graphlib`:mod:.  Refer to the standard documentation.

- Add function `xotl.tools.future.itertools.zip_map`:func:.
