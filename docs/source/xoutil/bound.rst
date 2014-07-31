======================================================================
 :mod:`xoutil.bound` -- Helpers for bounded execution of co-routines.
======================================================================

.. module:: xoutil.bound

.. versionadded:: 1.6.2

.. warning:: This is a development.  The API is flux.


A bounded execution model
=========================

Some functions are easy to implement using a generator (:pep:`342`).  Or
sometimes you'd want to "report units of work" one at a time.  These functions
could be easily programmed without any `bounds` whatsoever, and then you might
"weave" the bounds.

This module helps to separate the work-doing function from the boundary-tests
definitions.

This document uses the following terminology:

.. glossary::

   unbounded function

      This is the function that does the actual work without testing for any
      `boundary condition`:term:.

      This function *must* return a generator, called the `unbounded
      generator`:term:.

   unbounded generator

      The generator returned by an `unbounded function`:term:.  This generator
      is allowed to yield forever, although it could terminate by itself.  So
      this is actually a `possibly` unbounded generator, but we keep the term
      to emphasize.

   boundary condition

      Is a condition that can be tested, when met it indicates that the
      `unbounded generator`:term: should be closed.

      A boundary condition is usually implemented in a single function called
      a `boundary definition`:term:.

   boundary definition

      A function that tests whether a boundary condition has met.  This
      function must comply with the boundary protocol (see `boundary`:func:).

      Sometime we identify the `boundary` with its `boundary definition`.

   bounded function

      Is the result of applying a `boundary definition` to an `unbounded
      function`.

   bounded generator

      Is the result of applying a `boundary condition` to an `unbounded
      generator`.


See below__ for clarification of these terms and why the matter.

__ `Defining boundaries`_.

The bounded execution model takes at least an `unbounded generator` and a
`boundary condition` (which as stated `above <boundary condition>`:term: is
also a generator).  Applying the boundary condition to the generator
ultimately results in a bounded generator, which will be semantically
equivalent to the `unbounded generator` but will stop yielding when the
boundary condition yields True or when the generator itself is exhausted.


Included boundary conditions
----------------------------

.. autofunction:: timed(maxtime)

.. autofunction:: times(n)

.. autofunction:: accumulated(mass, *attrs, initial=0)

.. autofunction:: pred(func, skipargs=True)


Chaining several boundary conditions
------------------------------------

To created a more complex boundary than the one provided by a single condition
you could use the following high-level boundaries:

.. autofunction:: whenany(*boundaries)

.. autofunction:: whenall(*boundaries)


An example: time bounded batch processing
-----------------------------------------

We have a project in which we need to send emails inside a `cron` task
(celery_ is not available).  Emails to be sent are placed inside an `Outbox`
but we may only spent about 60 seconds to send as many emails as we can.  If
our emails are reasonably small (i.e will be delivered to the SMTP server in a
few miliseconds) we could use the `timed`:func: predicate to bound the
execution of the task::


    @timed(50)
    def send_emails():
       outbox = Outbox.open()
       try:
          for message in outbox:
	     emailbackend.send(message)
	     outbox.remove(message)
	     yield message
       finally:
          outbox.close()  # actually remove sent messages

Notice that you **must** enclose your batch-processing code in a ``try``
statement if you need to somehow commit changes.  Since we may call the
``close()`` method of the generator to signal that it must stop.

A ``finally`` clause is not always appropriated cause an error that is not
GeneratorExit error should not commit the data unless you're sure data changes
that were made before the error could be produced.  In the code above the only
place in the code above where an error could happen is the sending of the
email, and the data is only touched for each email that is actually sent.  So
we can safely close our outbox and commit the removal of previous message from
the outbox.


Defining boundaries
-------------------

.. autofunction:: boundary(definition)


Let's explain in detail the implementation of `timed`:func: as an example of
how a boundary condition could be implemented.


.. code-block:: python
   :linenos:

   @boundary
   def timed(maxtime):
       from datetime import datetime, timedelta
       if isinstance(maxtime, timedelta):
	   bound = maxtime
       else:
	   bound = timedelta(seconds=maxtime)
       start = datetime.now()
       yield False  # The first `sent` with args, kwargs
       while datetime.now() - start < bound:
	   yield False  # we still hace time
       yield True   # Inform the boundary condition, or we're not compliant
                    # with the boundary protocol.

The `timed` function (before application of `boundary`:func:) is what we call
a `boundary definition`:term:.  The generator returned by this function is the
`boundary condition`:term:.  After the application of ``boundary()``, this is
actually a `BoundaryCondition`:class: instance.

When applied this boundary to, say, the `fibonacci` implementation:

.. code-block:: python
   :linenos:

   def fibonacci():
       a, b = 1, 1
       while True:
          yield a
	  a, b = b, a + b



Internal API
============

.. autoclass:: Bounded
   :members: __call__, generate

   This class is actually subclassed inside the
   `~BoundaryCondition.apply`:meth: so that the weaving boundary definition
   with the `target` unbounded function is not exposed.

.. autoclass:: BoundaryCondition
   :members:

.. _celery: http://docs.celeryproject.org/
