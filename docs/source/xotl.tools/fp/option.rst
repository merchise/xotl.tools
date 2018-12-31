`xotl.tools.fp.option`:mod: - Functional Programming Option Type
================================================================

.. automodule:: xotl.tools.fp.option
   :members:


Further Notes
-------------

It could be thought that this kind of concept is useless in Python because the
dynamic nature of the language, but always there are certain logic systems
that need to wrap "correct" false values and "incorrect" true values.

Also, in functional programming, errors can be reasoned in a new way: more
like as *error values* than in *exception handling*.  Where the `Maybe`:class:
type expresses the failure possibility through `Wrong`:class: instances
encapsulating errors.

When receiving a `Wrong`:class: instance encapsulating an error, and want to
recover the *exception propagation style* -instead of continue in *pure
functional programming*-, to re-raise the exception, instead the `raise`
Python statement, use `~xotl.tools.eight.errors.throw`:func:.

See https://en.wikipedia.org/wiki/Monad_%28functional_programming%29#\
The_Maybe_monad
