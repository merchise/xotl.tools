Migrate features compliant with `six` concept to :mod:`xoutil.eight`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: Check all around `xoutil` and migrate to `xoutil.eight`:mod: all
	  tools that are related to write code that must be compatible with
	  Python 2 and 3 versions.

This task was already started by migrating:

- Meta-classes definition.  See `xoutil.eight.meta.metaclass`:func:.

- Definitions that exists in only one version (2 or 3) of Python module
  :mod:`types`.  See :mod:`xoutil.eight.types`.

.. todo:: Progressively update HISTORY file with all `xoutil.eight`:mod:
	  related progress.
