======================================================================
 :mod:`xoutil.bound` -- Helpers for bounded execution of co-routines.
======================================================================

.. module:: xoutil.bound

.. versionadded:: 1.6.3

.. warning:: This is a development.  The API is flux.


A bounded execution model
=========================

.. autofunction:: bounded(*preds, **namedpreds)(target)

.. autofunction:: predicate([name])(func)


Standard predicates for bounded execution
-----------------------------------------

.. autofunction:: pred

.. autofunction:: timed

.. autofunction:: times


Higher level predicates
-----------------------

.. autofunction:: whenany(*preds, **namedpreds)

.. autofunction:: whenall(*preds, **namedpreds)


An example: time bounded batch processing
-----------------------------------------

You may use this kind of bounded execution for some batch processing that must
be bounded, say, by time.

We have a project in which we need to send emails inside a `cron` task
(celery_ is not available).  Emails to be sent are placed inside an `Outbox`
but we may only spent about 60 seconds.  If our emails are reasonably small
(i.e will be delivered to the SMTP server in a few miliseconds) we could use
the `timed`:func: predicate to bound the execution of the task::


    @bounded(timed=50)
    def send_emails():
       try:
          for outgoing in Outbox:
	     emailbackend.send(outgoing)
	     outgoing.sent = True
	     yield outgoing
       finally:
          Outbox.close()

Notice that you **must** enclose your batch-processing code in a ``try``
statement if you need to somehow commit changes.  `bounded`:func: will the
``close()`` method of the generator at termination.

A ``finally`` clause is not always appropriated cause an error that is not a
GeneratorExit error should not commit the data unless you're sure data changes
that were made before the error can be committed.  In the code above the only
place in the code above where an error could happen is the sending of the
email, and the data is only touched for each email that is actually sent.


.. _celery: http://docs.celeryproject.org/
