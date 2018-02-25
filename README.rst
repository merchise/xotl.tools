`xoutil` is a collection of disparate utilities that does not conform a
framework for anything.  `xoutil` is essentially -but not exclusively- an
extension to the Python's standard library.

In `xoutil` you will probably find:

- Compatibility solvers for major versions issues\ [#another-six]_.  See
  `xoutil.eight`.

  .. note:: Starting with xoutil 2.0, support for Python 2 is no longer
     supported.  Although many things in the xoutil API remain just to avoid
     hard code-breaks, they won't work in Python 2 and many things will be
     deprecated.

- Tools that must be implemented in the Python Standard Library, but there are
  things that escape from the Guido's scope. ;)

- Components that belong naturally to the "Common Systems Layer" \
  [#continuum]_.

.. [#another-six] Yes!, yet another solution for this. ;)

.. [#continuum] http://pubs.opengroup.org/architecture/togaf9-doc/arch/chap39.html#tag_39_04_01
