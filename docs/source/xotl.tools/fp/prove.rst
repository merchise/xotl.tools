`xotl.tools.fp.prove`:mod: - Prove validity of values
=====================================================

Proving success or failure of a function call has two main patterns:

1. Predicative: a function call returns one or more values indicating a
   failure, for example method ``find`` in strings returns ``-1`` if the
   sub-string is not found.  In general this pattern considers a set of values
   as logical Boolean true, an other set false.

   Example::

     index = s.find('x')
     if index >= 0:
         ...    # condition of success
     else:
         ...    # condition of failure



2. Disruptive: a function call throws an exception on a failure breaking the
   normal flow of execution, for example method ``index`` in strings.

   Example::

     try:
         index = s.index('x)
     except ValueError:
         ...    # condition of failure
     else:
         ...    # condition of success

   The exception object contains the semantics of the ""anomalous condition".
   Exception handling can be used as flow control structures for execution
   context inter-layer processing, or as a termination condition.


Module content
--------------

.. automodule:: xotl.tools.fp.prove
   :members:
