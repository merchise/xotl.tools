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
a consistent import style, or give a name for the task.  Using `nameof` you
can easily fix this problem.

Assume you create a ``celapp.tasks.basic`` module with this code:

.. testsetup:: celapp.tasks.basic

   __name__ = 'celapp.tasks.basic'

.. doctest:: celapp.tasks.basic

   >>> def celery_task(celeryapp, *args, **kwargs):
   ...    def decorator(func):
   ...        from xotl.tools.names import nameof
   ...        taskname = nameof(func, full=True, inner=True)
   ...        return celeryapp.task(name=taskname, *args, **kwargs)(func)
   ...    return decorator

   >>> from celery import Celery
   >>> app = Celery()
   >>> @celery_task(app)
   ... def add(x, y):
   ...     return x + y

Then importing the task directly in a shell will have the correct name::

    >>> from celapp.tasks.basic import add
    >>> add.name
    'celapp.tasks.basic.add'

Another module that imports the task will also see the proper name.  Say you
have the module ``celapp.consumer``:


.. testsetup:: celapp.consumer

   __name__ = 'celapp.consumer'


.. doctest:: celapp.consumer

   >>> from .tasks import basic

   >>> def get_name(taskname):
   ...     task = getattr(basic, taskname)
   ...     return task.name

Then:

.. doctest::

   >>> from celapp.consumer import get_name
   >>> get_name('add')
   'celapp.tasks.basic.add'


Despite that you imported the ``basic`` module with a relative import the name
is fully calculated.


.. _Celery: http://celeryproject.org/
