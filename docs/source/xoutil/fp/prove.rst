`xoutil.fp.prove`:mod: - Prove validity of values
=================================================

.. module:: xoutil.fp.prove

.. sectionauthor:: Medardo Rodriguez <med@merchise.org>

--------------

There is an amalgam of mechanisms to validate function results in a "safe"
way when there are possibilities of failures.  The best, or more clear method,
is to raise an exception, but there are scenarios where a fail could be
signaled with "special values".

The function `vouch`:func: manage these scenarios raising an exception every
time a failure is detected.

Predicates (that which is affirmed or denied of a thing) are a complicated
case: most implementations return a Boolean value expressing validity of a
given argument.  In these cases, `vouch`:func: returns the value (not
``True``) if valid.

The `safe`:func: decorator could be used to mark any callable to be managed
with `vouch`:func:.


.. autofunction:: vouch

.. autoclass:: Coercer
