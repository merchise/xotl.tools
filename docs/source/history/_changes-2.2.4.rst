- Add the American spelling of `~xotl.tools.dim.base.Length.meter`:attr: to
  all units in `~xotl.tools.dim.base.Length`:class: and derived units
  (`~xotl.tools.dim.base.Velocity`:class:, etc).

  The was a bug in the documentation of non canonical units for
  `~xotl.tools.dim.base.Length`:class:, they were spelled in the documentation
  using the British spelling "metre", but the code actually used the US
  English spelling "meter"; now both spellings are available.

- Drop support for Python 3.6 completely.

- Change the CI pipeline to run mypy only in Python 3.10, and configure the
  distribution using ``setup.cfg`` driven metadata and options.
