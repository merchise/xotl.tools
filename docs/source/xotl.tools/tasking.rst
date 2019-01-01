===================================================
 :mod:`xotl.tools.tasking` -- Task oriented tools.
===================================================

.. automodule:: xotl.tools.tasking


.. autoclass:: retrier(max_tries=None, max_time=None, wait=DEFAULT_WAIT_INTERVAL, retry_only=None)
   :members: decorate

.. autofunction:: retry(fn, args=None, kwargs=None, *, max_tries=None, max_time=None, wait=DEFAULT_WAIT_INTERVAL, retry_only=None)

.. autoclass:: ConstantWait(wait=DEFAULT_WAIT_INTERVAL)

.. autoclass:: BackoffWait(wait=DEFAULT_WAIT_INTERVAL, backoff=1)

.. autodata:: MIN_WAIT_INTERVAL

.. autodata:: DEFAULT_WAIT_INTERVAL

.. class:: StandardWait

   A deprecated alias for `ConstantAlias`:class:.

.. autofunction:: get_backoff_wait
