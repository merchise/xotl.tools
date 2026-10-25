`xotl.tools.fp.option`:mod: - Functional Programming Option Type
================================================================

.. automodule:: xotl.tools.fp.option
   :members:

Migration guidance
==================

Prefer ordinary Python return values and exceptions over this module's combined option/error
wrapper protocol.  The entire module is deprecated without a promised removal version or
minimum retention period.

- Return successful values directly, including valid false values such as ``False``, ``0``, and
  empty containers.  Do not replace ``Just(value)`` with a truthiness test that treats these as
  failures.

- Use ``None`` for an absent result only when it cannot also be a valid result.  Otherwise use
  `xotl.tools.symbols.Unset`:obj: and compare it by identity with ``is Unset``, not equality or
  truthiness.  This keeps valid ``None``, ``False``, zero, and empty-container results distinct
  from absence:

  .. code-block:: python

     from xotl.tools.symbols import Unset

     value = mapping.get("key", Unset)
     if value is Unset:
         ...

  If ``Unset`` itself is a valid result, use a separate application-specific sentinel.

- Raise an appropriate exception for failures and handle it with ordinary ``try``/``except``.
  ``Wrong`` can contain either an exception or an arbitrary rejected value; decide explicitly
  which failure to raise rather than assuming every wrapped value is an exception.

- Once callers use ordinary values, remove calls to ``take`` and the ``compel``/``choose``
  helpers instead of introducing another implicit wrapping/unwrapping layer.

These are API migrations, not drop-in substitutions.  ``Just`` is true even when its contents
are false, ``Wrong`` is false even when its contents are true, and the singleton ``none`` is
not Python's ``None``.  Preserve those distinctions until callers have migrated deliberately.

Compatibility during deprecation
================================

This change preserves existing classes, signatures, wrapping and equality behavior, and the
identities of ``false``, ``true``, and ``none``.  Construction and public helpers emit on-use
warnings; importing the module to initialize its singletons does not itself warn.

The retained parameter-schema classes still use these wrappers and singletons.  Future removal
must first migrate that dependency without breaking their promised compatibility.  This is not
an independent removal-version promise for ``fp.option``.

The unfinished ``choose`` helper retains its existing behavior; deprecation does not implement
or repair it.
