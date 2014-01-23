:mod:`xoutil.fs` -- file system utilities
=========================================

.. automodule:: xoutil.fs
   :members: ensure_filename, imap, iter_dirs, iter_files, listdir, rmdirs,
	     stat, walk_up

.. function:: makedirs(path, mode=0o777, exist_ok=False)

   Recursive directory creation function. Like :py:func:`os.mkdir`, but makes
   all intermediate-level directories needed to contain the leaf directory.

   The default mode is 0o777 (octal). On some systems, mode is ignored. Where
   it is used, the current umask value is first masked out.

   If `exist_ok` is False (the default), an OSError is raised if the target
   directory already exists. If `exist_ok` is True an OSError is still raised
   if the umask-masked mode is different from the existing mode, on systems
   where the mode is used. OSError will also be raised if the directory
   creation fails.

   .. note:: :func:`makedirs` will become confused if the path elements to
             create include :py:data:`os.pardir` (eg. ".." on UNIX systems).

   This function handles UNC paths correctly.


   .. note:: This is a port of Python 3.3 standard :py:func:`os.makedirs`.

	     In Python 3.3+ this is the same function of the standard library.


Contents:

.. toctree::
   :maxdepth: 1

   fs/path
