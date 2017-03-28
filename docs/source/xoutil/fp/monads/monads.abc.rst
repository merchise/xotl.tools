==========================================
 ``xoutil.fp.monads.abc`` -- Monadic ABCs
==========================================

.. automodule:: xoutil.fp.monads.abc
   :members:


Understanding Monads
====================

.. note:: Many of this documentation is based on "Haskell Programming
          Language" `book <http://wikibooks.org>`_.


Functor
-------

**Class definition**: The `xoutil.fp.monads.abc.Functor`:class: class defines
the interface for types which can be mapped over.  In Haskell, it has a single
method, called ``fmap``.  The class is defined as follows::

  class Functor f where
    fmap :: (a -> b) -> f a -> f b

For example (in Haskell)::

  λ> fmap (\x -> x + 1) [1..3]
  [2,3,4]


.. attention:: Yes!, Haskell lists are monadic; and yes!, I use "λ" as my
               `GHCi` prompt.

Formally speaking, ``fmap`` is a generalization of ``map`` for any
parametrized data types.  Functor ``map`` must know how to apply functions to
values that are wrapped in any monadic context.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Haskell
     - Python

   * - ``fmap`` (``<$>``)
     - ``map`` (using ``%`` as reversed infix version).  For example::

         >>> (lambda x: 2*x + 1) % Just(1)
         3

**The functor laws**: `~xoutil.fp.monads.abc.Functor`:class: instances should
satisfy the following laws:

#. Mapping ``id``\ [#fid]_ over a functor must return the functor unchanged::

     fmap id == id

#. Should not matter whether we map a composed function or first map one
   function and then the other::

     fmap (f . g)  ==  fmap f . fmap g

.. [#fid] Identity function, which returns its argument unaltered.

In Python these laws are expressed as::

  x.map(id) == id(x)
  x.map(compose(f, g)) == x.map(g).map(f)


Monoid
------

**Class definition**: The `xoutil.fp.monads.abc.Monoid`:class: class define an
associative operation which combines two elements and a "zero" value which
acts as neutral element for the operation.

  class Monoid a where
    mempty  :: a
    mappend :: a -> a -> a
    mconcat :: [a] -> a

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Haskell
     - Python

   * - ``mempty``
     - ``empty``

   * - ``mappend``
     - ``append``

   * - ``mconcat``
     - ``concat`` (using ``+`` as infix version)

**The Monoid laws**: `~xoutil.fp.monads.abc.Monoid`:class: instances also have
laws really simple, though; corresponding to the neutral element and mentioned
associative properties::

   mappend mempty x = x
   mappend x mempty = x
   mappend x (mappend y z) = mappend (mappend x y) z
   mconcat = foldr mappend mempty


Applicative functor
-------------------

**Class definition**: The `xoutil.fp.monads.abc.Applicative`:class: class
defines functors with some extra properties.  You can apply functions inside a
functor to values that can be inside the functor or not.  The class is defined
as follows::

  class (Functor f) => Applicative f where
    pure  :: a -> f a
    (<*>) :: f (a -> b) -> f a -> f b

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Haskell
     - Python

   * - ``pure``
     - ``pure``

   * - ``(<*>)``
     - ``apply`` (using ``*`` as infix version)

**The Applicative functor laws**: `~xoutil.fp.monads.abc.Applicative`:class:
instances should satisfy the following laws::

  pure id <*> v = v                            -- Identity
  pure (.) <*> u <*> v <*> w = u <*> (v <*> w) -- Composition
  pure f <*> pure x = pure (f x)               -- Homomorphism
  u <*> pure y = pure ($ y) <*> u              -- Interchange

And the Functor instance should satisfy the following law::

  fmap f x = pure f <*> x                      -- Fmap


`Maybe` Example
~~~~~~~~~~~~~~~

As we have seen the ``Functor`` instance of ``Maybe``, let's try to make it
``Applicative`` as well.

The definition of ``pure`` is easy.  It is ``Just``.  Now the definition of
``(<*>)``.  If any of the two arguments is ``Nothing``, the result should be
``Nothing``.  Otherwise, we extract the function and its argument from the two
``Just`` values, and return ``Just`` the function applied to its argument::

  instance Applicative Maybe where
    pure = Just
    (Just f) <*> (Just x) = Just (f x)
    _        <*> _        = Nothing


Monad
-----

Since monads have so many applications (any imperative *sequence of
operations*), they are often explained from a particular *point of view*,
which can reduce the understanding in their full power.

**Class definition**: The `xoutil.fp.monads.abc.Monad`:class: class is defined
by three things:

- a type constructor ``M``;
- a function ``return``; and
- an operator ``(>>=)`` which is pronounced "bind".

::

  class Monad m where
    return :: a -> m a
    (>>=)  :: m a-> (a -> m b) -> m b
    (>>)   :: m a -> m b -> m b
    fail   :: String -> m a

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Haskell
     - Python

   * - ``return``
     - ``unit``

   * - ``>>=``
     - ``bind`` (using ``>>`` as infix version)

   * - ``>>``
     - ``then`` (trivial in Python)

   * - ``fail``
     - (not needed in Python)

Iin Haskell, function ``fail`` handles pattern match failures in ``do``
notation; in Python, use context managers and/or exceptions.

**The Monad laws**: `~xoutil.fp.monads.abc.Applicative`:class: instances is
expected to obey the following three laws::

  m >>= return    = m                          -- right unit
  return x >>= f  = f x                        -- left unit
  (m >>= f) >>= g = m >>= (\x -> f x >>= g)    -- associativity

The Monad doesn't specify what is happening, only that whatever is happening
satisfies the laws of associativity and identity.


CategoricalMonad
----------------

Monads come from *Category Theory* (a branch of mathematics).  Fortunately, it
isn't necessary to understand completely that math theory in order to
understand monads in functional programming.

**Class definition**: The `xoutil.fp.monads.abc.CategoricalMonad`:class: class
is defined slightly different (as in *Category Theory*):

  fmap   :: (a -> b) -> M a -> M b    -- functor
  return :: a -> M a
  join   :: M (M a) -> M a

That functions act as:

- ``fmap``: applies a given function to every element in a container,
- ``return``: packages an element into a container,
- ``join``: takes a container of containers and turns them into a single
  container.

A definition of ``fmap`` and ``join`` could be given in terms of ``bind``
(``>>=``) and ``return``::

  fmap f x = x >>= (return . f)
  join x   = x >>= id

According to *Category Theory*, all monads are by definition functors too.
However, in Haskell it is different, and the ``Monad`` class has actually
nothing to do with the ``Functor`` class.  We, in Python, defined the
`xoutil.fp.monads.abc.CategoricalMonad`:class: class to remove this condition
and also to have a single class to inherits from it in most common monadic
implementations.

`Monadic` is an alias to this base class.
