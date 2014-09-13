======================================================================
 :mod:`xoutil.bound` -- Helpers for bounded execution of co-routines.
======================================================================

.. module:: xoutil.bound

.. versionadded:: 1.6.3  Pre-release version.

.. warning:: This module is still in heavy development.  The API is flux.  It
   will be declared stable only after release 1.7.0.  Even the module name
   might change in the future.


A bounded execution model
=========================

Some features are easy to implement using a generator or co-routine
(:pep:`342`).  For instance, you might want to "report units of work" one at a
time.  These kind of features could be easily programmed without any `bounds`
whatsoever, and then you might "weave" the bounds.

This module helps to separate the work-doing function from the boundary-tests
definitions.

This document uses the following terminology:

.. glossary::

   unbounded function

      This is the function that does the actual work without testing for any
      `boundary condition`:term:.  Boundary conditions are not
      "natural-causes" of termination for the algorithm but conditions imposed
      elsewhere: the environment, resource management, etc.

      This function *must* return a generator, called the `unbounded
      generator`:term:.

   unbounded generator

      The generator returned by an `unbounded function`:term:.  This generator
      is allowed to yield forever, although it could terminate by itself.  So
      this is actually a `possibly` unbounded generator, but we keep the term
      to emphasize.

   boundary condition

      Is a condition, imposed outside the logical description of any
      algorithm, that can be tested, when met it indicates that the `unbounded
      generator`:term: should be closed.  The boundary condition is tested
      each time the unbounded generator yields.

      A boundary condition is usually implemented in a single function called
      a `boundary definition`:term:.

   boundary definition

      A function that implements a boundary condition.  This function must
      comply with the boundary protocol (see `boundary`:func:).

      Sometime we identify the `boundary` with its `boundary definition`.

   bounded function

      Is the result of applying a `boundary definition` to an `unbounded
      function`.

   bounded generator

      Is the result of applying a `boundary condition` to an `unbounded
      generator`.


__ `Defining boundaries`_.

The bounded execution model takes at least an `unbounded generator` and a
`boundary condition` (which as stated `above <boundary condition>`:term: is
also a generator).  Applying the boundary condition to the generator
ultimately results in a bounded generator, which will be semantically
equivalent to the `unbounded generator` but will stop yielding when the
boundary condition yields True or when the generator itself is exhausted.


Included boundary conditions
============================

.. autofunction:: timed(maxtime)

.. autofunction:: times(n)

.. autofunction:: accumulated(mass, *attrs, initial=0)

.. autofunction:: pred(func, skipargs=True)


Chaining several boundary conditions
====================================

To created a more complex boundary than the one provided by a single condition
you could use the following high-level boundaries:

.. autofunction:: whenany(*boundaries)

.. autofunction:: whenall(*boundaries)



Defining boundaries
===================

If none of the boundaries defined deals with a boundary condition you have,
you may create another one using `boundary`:func:.  This is usually employed
as decorator on the `boundary definition`:term:.

.. autofunction:: boundary(definition)


Illustration of a boundary
--------------------------

Let's explain in detail the implementation of `times`:func: as an example of
how a boundary condition could be implemented.


.. code-block:: python
   :linenos:

   @boundary
   def times(n):
       '''Becomes True after a given the `nth` item have been produced.'''
       passed = 0
       yield False
       while passed < n:
	   yield False
	   passed += 1
       yield True

We implemented the boundary condition via the `boundary`:func: helper.  This
helpers allows to implement the boundary condition via a boundary definition
(the function above).  Then the ``boundary`` helper takes the definition it
builds a `BoundaryCondition`:class: instance.  This instance can then be used
to decorate the `unbounded function`, this operation returns a `bounded
function` (a `Bounded`:class: instance).

When the `bounded function` is called, what actually happens is that:

- First the boundary condition is invoked passing the ``n`` argument, and thus
  we obtain the generator from the ``times`` function.

- We also get the generator from the unbounded function.

- Then we call ``next(boundary)`` to allow the ``times`` boundary to
  initialize itself.  This runs the code of the ``times`` definition up to the
  line 5 (the first ``yield`` statement).

- The `bounded function` ignores the message from the boundary at this point.

- Then it sends the arguments passed to original function via the ``send()``
  method of the boundary condition generator.

- This unfreezes the boundary condition that now tests whether ``passes`` is
  less that ``n``.  If this is true, the boundary yields False and suspends
  there at line 7.

- The `bounded function` see that message is not True and asks the `unbounded
  generator` for its next value.

- Then it sends that value to the boundary condition generator, which resumes
  execution at line 8.  The value sent is ignored and ``passes`` gets
  incremented by 1.

- Again the generator asks if ``passes`` is less that ``n``.  If passes has
  reached ``n``, it will execute line 9, yielding True.

- The `bounded function` see that the boundary condition is True and calls the
  ``close()`` method to the boundary condition generator.

- This is like raising a GeneratorExit just after resuming the ``times`` below
  line 9.  The error is not trapped and propagates the ``close()`` method of
  the generator knows this means the generator has properly finished.

  .. note:: Other boundaries might need to deal with GeneratorExit explicitly.

- Then the `bounded function` regains control and calls the ``close()`` method
  of the `unbounded generator`, this effectively raises a GeneratorExit inside
  the unbounded generator, which if untreated means everything went well.


If you look at the implementation of the `included boundary conditions`_,
you'll see that all have the same pattern:

a) Initialization code, followed by a ``yield False`` statement.  This is a
   clear indicator that the included boundary conditions disregard the first
   message (the arguments to the unbounded function).

b) A looping structure that tests the condition has not been met and yields
   False at each cycle.

c) The ``yield True`` statement outside the loop to indicate the boundary
   condition has been met.

This pattern is not an accident.  As an exception see the code for
`whenall`:func: and `whenany`:func:.  They lack the first standalone `yield
False` because they must not assume all its subordinate predicates will ignore
the first message.


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


An example: time bounded batch processing
=========================================

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
       except GeneratorExit:
          pass  # Avoid the propagation of this
       finally:
          outbox.close()  # commit the changes to the outbox

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
