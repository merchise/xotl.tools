:mod:`xoutil.logger` - Standard logger helpers
==============================================

.. module:: xoutil.logger

Usage::

    logger.debug('Some debug message')


Basically you may request any of the loggers attribute/method and this
module will return the logger's attribute corresponding to the loggers of
the calling module.  This avoids the boilerplate seen in most codes::

    logger = logging.getLogger(__name__)


You may simply do::

    from xoutil.logger import debug
    debug('Some debug message')

The proper logger will be selected by this module.


.. note:: Notice this won't configure any handler for you.  Only the calling
	  pattern is affected.  You must configure your loggers as usual.
