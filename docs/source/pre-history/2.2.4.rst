- Add functions:

  - `~xotl.tools.future.datetime.get_next_monday`:func:,
  - `~xotl.tools.future.datetime.get_next_tuesday`:func:,
  - `~xotl.tools.future.datetime.get_next_wednesday`:func:,
  - `~xotl.tools.future.datetime.get_next_thursday`:func:,
  - `~xotl.tools.future.datetime.get_next_friday`:func:,
  - `~xotl.tools.future.datetime.get_next_saturday`:func:,
  - `~xotl.tools.future.datetime.get_next_sunday`:func:,
  - `~xotl.tools.future.datetime.get_previous_monday`:func:,
  - `~xotl.tools.future.datetime.get_previous_tuesday`:func:,
  - `~xotl.tools.future.datetime.get_previous_wednesday`:func:,
  - `~xotl.tools.future.datetime.get_previous_thursday`:func:,
  - `~xotl.tools.future.datetime.get_previous_friday`:func:,
  - `~xotl.tools.future.datetime.get_previous_saturday`:func:, and
  - `~xotl.tools.future.datetime.get_previous_sunday`:func:.

- Add the American spelling of `~xotl.tools.dim.base.Length.meter`:attr: to
  all units in `~xotl.tools.dim.base.Length`:class: and derived units
  (`~xotl.tools.dim.base.Velocity`:class:, etc).

  The was a bug in the documentation of non canonical units for
  `~xotl.tools.dim.base.Length`:class:, they were spelled in the documentation
  using the British spelling "metre", but the code actually used the US
  English spelling "meter"; now both spellings are available.

- Drop support for Python 3.6 completely.
