Study notes about Monads
========================

2016-09-22
----------

- For our purposes, a monad consists of a type constructor ``M`` and two
  operations:

  - ``unit :: a -> Ma``

  - ``(*) :: Ma -> (a -> Mb) -> Mb``

  We write ``::`` for "has type".  If you are a functional programmer, think
  of ``M`` as a type constructor in a functional language, and ``unit`` and
  ``*`` as polymorphic functions.  If you are a domain theorist, think of
  ``M`` as an operation on domains, and ``unit`` and ``*`` as operations
  parameterised on the domains ``a`` and ``b``.

  The monad operations must satisfy three laws:

  - left unit::

      unit v * (λ w. k w) = k v

  - right unit::

      m * (λ v. unit v) = m``

  - associative::

      m * (λ v. k v)) * (λ w. h w) = m * (λ v. (k v * (λ w. h w)))

  .. biblio_ref(title="Monads and composable continuations",
                section="2. Monads", page=3)


2016-09-25
----------

In Wikipedia\ [#wiki]_: In mathematics, a **predicate** is commonly understood
to be a Boolean-valued function ``P: X -> {true, false}``, called the
predicate on ``X``.  However, predicates have many different uses and
interpretations in mathematics and logic, and their precise definition,
meaning and use will vary from theory to theory.  So, for example, when a
theory defines the concept of a relation, then a predicate is simply the
**characteristic function** or the **indicator function** of a relation.
However, not all theories have relations, or are founded on set theory, and so
one must be careful with the proper definition and semantic interpretation of
a predicate.

.. [#wiki] http://en.wikipedia.org/wiki/Predicate_%28mathematical_logic%29
