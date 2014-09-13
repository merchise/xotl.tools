:mod:`xoutil.fs` -- file system utilities
=========================================

.. automodule:: xoutil.fs
   :members: ensure_filename, imap, iter_dirs, iter_files,
	     listdir, rmdirs, stat, walk_up

.. autofunction:: concatfiles(*files, target)

.. function:: makedirs(path, mode=0o777, exist_ok=False)

   Recursive directory creation function.  Like :func:`os.mkdir`, but makes
   all intermediate-level directories needed to contain the leaf directory.

   The default *mode* is ``0o777`` (octal).  On some systems, *mode* is
   ignored.  Where it is used, the current umask value is first masked out.

   If *exist_ok* is ``False`` (the default), an :exc:`OSError` is raised if
   the target directory already exists.

   .. note:: :func:`makedirs` will become confused if the path elements to
             create include :py:data:`os.pardir` (eg. ".." on UNIX systems).

   This function handles UNC paths correctly.


   .. versionchanged:: 1.6.1  Behaves as Python 3.4.1.

      Before Python 3.4.1 (ie. xoutil 1.6.1), if *exist_ok* was ``True`` and
      the directory existed, :func:`makedirs` would still raise an error if
      *mode* did not match the mode of the existing directory. Since this
      behavior was impossible to implement safely, it was removed in Python
      3.4.1. See the original :py:func:`os.makedirs`.


Contents:

.. toctree::
   :maxdepth: 1

   fs/path
