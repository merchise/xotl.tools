================================================================================
:mod:`xoutil.decorator.compat` -- Decorators for Python 2 and 3 interoperability
================================================================================

.. automodule:: xoutil.decorator.compat

.. autofunction:: metaclass(meta)

   .. warning::

      *Deprecated since 1.4.1*, and it will be **removed in 1.4.2!** because of
      a bug. You should use :func:`xoutil.objects.metaclass`.

      The bug happens precisely because this *is a decorator*: since the class
      is created before is passed to decorator; a metaclass with has
      side-effects (like registration) won't work properly with this decorator.

      Example of the bug::

            class RegisteringType(type):
                classes = []

                def __new__(cls, name, bases, attrs):
                    res = super(RegisteringType, cls).__new__(cls, name, bases, attrs)
                    cls.classes.append(res)  # <--- registers the new class
                    return res

            @metaclass(RegisteringType)
            class Base(object):
                pass

            class SubType(RegisteringType):
                def __new__(cls, name, bases, attrs):
                    return super(SubType, cls).__new__(cls, name, bases, attrs)

            @metaclass(SubType)
            class Foo(Base):
                pass

      ``RegisteringType`` adds all its instances to ``classes``, so you'd
      expect that only ``Base`` and ``Foo`` are there, but since ``Foo`` is
      actually created two times (before and after the decorator) there are
      **three** classes registered.
