=================================================================
 `xotl.tools.names`:mod: -- Utilities for handling objects names
=================================================================

.. automodule:: xotl.tools.names

.. autofunction:: nameof(*objects, depth=1, inner=False, typed=False, full=False, safe=False)

.. autofunction:: identifier_from(obj)


.. _name-of-narrative:

Use cases for getting the name of an object
===========================================

The function `nameof`:func: is useful for cases when you get a value and you
need a name.  This is a common need when doing framework-level code that tries
to avoid repetition of concepts.


Solutions with `nameof`:func:
-----------------------------

Properly calculate the tasks' name in Celery applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Celery_ warns about how to import the tasks.  If in a module you import your
task using an absolute import, and in another module you import it using a
relative import, Celery regards them as different tasks.  You must either use
a consistent import style, or give a name for the task.  Using `nameof`:func:
you can easily fix this problem.

.. _Celery: http://celeryproject.org/
