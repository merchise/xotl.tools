- Now `xoutil` supports Python 2.7, and 3.1+.  Python 3.0 was not tested.

- Added a `strict` parameter to `xoutil.objects.smart_getter`:func:.

- New function `xoutil.objects.get_traverser`:func:.

- The function `xoutil.cli.app.main`:func: prefers its `default` parameter
  instead of the application's default command.

  Allow the `xoutil.cli.Command`:class: to define a ``command_cli_name`` to
  change the name of the command.  See `xoutil.cli.tools.command_name`:func:.
