======================================================================
 `xoutil.dim.app.standard`:mod: - The standard `physical quantities`_
======================================================================

.. automodule:: xoutil.dim.app.standard

.. autoclass:: Length

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


.. autoclass:: Time

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


.. autoclass:: Mass

   The Mass base quantity.

   .. attribute:: kilogram

      The canonical unit.

   .. attribute:: kg

      An alias of `kilogram`:attr:

   Other attributes:

   .. attribute:: gram


.. autoclass:: ElectricCurrent

   The electrical current base quantity.

   .. attribute:: ampere

      The canonical unit.

   .. attribute:: A

      An alias of `ampere`:attr:


.. autoclass:: Temperature

   The thermodynamic temperature base quantity.

   .. attribute:: kelvin

      The canonical unit.

   .. attribute:: K

      An alias of `kelvin`:attr:


   .. automethod:: from_celcius

   .. automethod:: from_fahrenheit


.. autoclass:: Substance

   The amount of substance.

   .. attribute:: mole

   .. attribute:: mol

      An alias of `mole`:attr:.


.. autoclass:: Luminosity

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

.. class:: Volume

   Defined as `L`:class:\ ``**3``.

.. class:: Frequency

   Defined as `T`:class:\ ``**-1`` (which is the same as ``1/T``).

.. class:: Force

   Defined as `L`:class: ``*`` `M`:class: ``*`` `T`:class:\ ``**-2``.

.. class:: Presure

   Defined as `L`:class:\ ``**-1 *`` `M`:class: ``*`` `T`:class:\ ``**-2``.

.. class:: Velocity

   Defined as `L`:class: ``*`` `T`:class:\ ``**-1``.

.. class:: Acceleration

   Defined as `L`:class: ``*`` `T`:class:\ ``**-2``.
