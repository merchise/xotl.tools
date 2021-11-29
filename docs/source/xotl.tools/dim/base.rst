==============================================================
 `xotl.tools.dim.base`:mod: - The base `physical quantities`_
==============================================================

.. automodule:: xotl.tools.dim.base

.. class:: Length

   The Length base quantity.

   .. attribute:: metre

      The canonical unit.

   .. attribute:: m

      An alias of `metre`:attr:

   Other attributes:

   .. attribute:: kilometre
   .. attribute:: km
   .. attribute:: centimetre
   .. attribute:: cm
   .. attribute:: millimetre
   .. attribute:: mm
   .. attribute:: nanometre
   .. attribute:: nm


.. class:: Time

   The Time base quantity.

   .. attribute:: second

      The canonical unit.

   .. attribute:: s

      An alias of `second`:attr:

   Other attributes:

   .. attribute:: millisecond
   .. attribute:: ms
   .. attribute:: nanosecond
   .. attribute:: ns
   .. attribute:: minute
   .. attribute:: hour


.. class:: Mass

   The Mass base quantity.

   .. attribute:: kilogram

      The canonical unit.

   .. attribute:: kg

      An alias of `kilogram`:attr:

   Other attributes:

   .. attribute:: gram


.. class:: ElectricCurrent

   The electrical current base quantity.

   .. attribute:: ampere

      The canonical unit.

   .. attribute:: A

      An alias of `ampere`:attr:


.. class:: Temperature

   The thermodynamic temperature base quantity.

   .. attribute:: kelvin

      The canonical unit.

   .. attribute:: K

      An alias of `kelvin`:attr:


   .. automethod:: from_celcius

   .. automethod:: from_fahrenheit


.. class:: Substance

   The amount of substance.

   .. attribute:: mole

   .. attribute:: mol

      An alias of `mole`:attr:.


.. class:: Luminosity

   The luminous intensity base quantity.

   .. attribute:: candela



Aliases
=======

.. class:: L

   An alias of `Length`:class:


.. class:: T

   An alias of `Time`:class:


.. class:: M

   An alias of `Mass`:class:


.. class:: I

   An alias of `ElectricCurrent`:class:


.. class:: O

   An alias of `Temperature`:class:.  We can't really use the Greek Theta Θ


.. class:: N

   An alias of `Substance`:class:


.. class:: J

   An alias of `Luminosity`:class:



Derived quantities
==================

.. class:: Area

   Defined as `L`:class:\ ``**2``.

   .. attribute:: metre_squared

      The canonical unit.

.. class:: Volume

   Defined as `L`:class:\ ``**3``.

   .. attribute:: metre_cubic

      The canonical unit.


.. class:: Frequency

   Defined as `T`:class:\ ``**-1`` (which is the same as ``1/T``).

   .. attribute:: unit_per_second

      The canonical unit.

   Aliases of the canonical unit:

   .. attribute:: Hz


.. class:: Force

   Defined as `L`:class: ``*`` `M`:class: ``*`` `T`:class:\ ``**-2``.

   .. attribute:: metre_kilogram_per_second_squared

      The canonical unit.

   Aliases of the canonical unit:

   .. attribute:: N
   .. attribute:: Newton

.. class:: Pressure

   Defined as `L`:class:\ ``**-1 *`` `M`:class: ``*`` `T`:class:\ ``**-2``.

   .. attribute:: kilogram_per_metre_per_second_squared

   Aliases of the canonical unit:

   .. attribute:: pascal
   .. attribute:: Pa

   .. versionchanged:: 2.1.11 Corrected the name from 'Presure' to 'Pressure'.
      You can still import the mistyped name.

.. class:: Velocity

   Defined as `L`:class: ``*`` `T`:class:\ ``**-1``.

   .. attribute:: metre_per_second

      The canonical unit.

.. class:: Acceleration

   Defined as `L`:class: ``*`` `T`:class:\ ``**-2``.

   .. attribute:: metre_per_second_squared

      The canonical unit.


On the automatically created names for derived quantities
=========================================================

We automatically create the name of the canonical unit of quantities derived
from others by simple rules:

- ``A * B`` joins the canonical unit names together with a low dash '_'
  in-between.  Let's represent it as `a_b`, where `a` stands for the name of
  the canonical unit of ``A`` and `b`, the canonical unit of ``B``.

  For the case, ``A * A`` the unit name is `a_squared`.

- ``A/B`` gets the name `a_per_b`.  ``1/A`` gets the name `unit_per_a`

- ``A**n``; when ``n=1`` this is the same as ``A``; when ``n=2`` this is the
  same as ``A * A``; for other positive values of ``n``, the canonical unit
  name is `a_pow_n`; for negative values of ``n`` is the same as ``1/A**n``;
  for ``n=0`` this is the `~xotl.tools.dim.meta.Scalar`:class: quantity.
