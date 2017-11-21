===============================================
 :mod:`xoutil.tasking` -- Task oriented tools.
===============================================

.. automodule:: xoutil.tasking


.. autofunction:: dispatcher(max_tries=None, max_time=None, wait=DEFAULT_WAIT_INTERVAL, retry_only=None)

.. autofunction:: dispatch(fn, args=None, kwargs=None, *, max_tries=None, max_time=None, wait=DEFAULT_WAIT_INTERVAL, retry_only=None)

.. autoclass:: StandardWait(wait=DEFAULT_WAIT_INTERVAL)

.. autoclass:: BackoffWait(wait=DEFAULT_WAIT_INTERVAL)

.. autodata:: MIN_WAIT_INTERVAL

.. autodata:: DEFAULT_WAIT_INTERVAL
