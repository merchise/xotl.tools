`xotl.tools.fs`:mod: -- file system utilities
=============================================

.. automodule:: xotl.tools.fs
   :members: ensure_filename, imap, iter_dirs, iter_files,
	     listdir, rmdirs, stat, walk_up

.. autofunction:: concatfiles(*files, target)

.. function:: makedirs(path, mode=0o777, exist_ok=False)

   Recursive directory creation function.  Like `os.mkdir`:func:, but makes
   all intermediate-level directories needed to contain the leaf directory.

   The default *mode* is ``0o777`` (octal).  On some systems, *mode* is
   ignored.  Where it is used, the current umask value is first masked out.

   If *exist_ok* is ``False`` (the default), an `OSError`:exc: is raised if
   the target directory already exists.

   .. note:: `makedirs`:func: will become confused if the path elements to
             create include `os.pardir`:py:data: (eg. ".." on UNIX systems).

   This function handles UNC paths correctly.

   .. versionchanged:: 1.6.1  Behaves as Python 3.4.1.

      Before Python 3.4.1 (ie. xotl.tools 1.6.1), if *exist_ok* was ``True``
      and the directory existed, `makedirs`:func: would still raise an error
      if *mode* did not match the mode of the existing directory. Since this
      behavior was impossible to implement safely, it was removed in Python
      3.4.1. See the original `os.makedirs`:py:func:.


Contents:

.. toctree::
   :maxdepth: 1

   fs/path
