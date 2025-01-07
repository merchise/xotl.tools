import difflib
import doctest
import importlib
import pprint
import typing as t
import unittest
from types import ModuleType

from .capture import captured_stderr, captured_stdout


class ExtendedBaseTestCase(unittest.TestCase):
    """Basic extensions to `unittest.TestCase`:class:

    .. versionadded:: 3.2.0

    """

    def runModuleDoctest(
        self,
        mod_or_name,
        *,
        additional_globals: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        """Run the doctests of the given module.

        All the symbols imported and/or defined in such module will be available
        to the doctests, additional symbols can be provided with
        `additional_globals`.

        All tests are run with NORMALIZE_WHITESPACE and ELLIPSIS.

        """
        run_module_doctest(mod_or_name, additional_globals=additional_globals)

    def assertDictKVMembers(self, mapping: t.Mapping, **expected):
        """Assert `mapping` has the expected key-value pairs (and possibly more)."""

        class _missing:
            def __repr__(self):
                return "<missing>"

        missing = _missing()

        actual_sequence = expected_sequence = t.cast(t.Tuple[t.Any, ...], ())
        for key, expected_value in expected.items():
            expected_sequence += ((key, expected_value),)
            try:
                actual_value = mapping[key]
            except KeyError:
                actual_sequence += ((key, missing),)
            else:
                actual_sequence += ((key, actual_value),)

        if actual_sequence != expected_sequence:
            diff = "\n" + "\n".join(
                difflib.ndiff(
                    pprint.pformat(expected_sequence).splitlines(),
                    pprint.pformat(actual_sequence).splitlines(),
                )
            )
            additional_values = {k: v for k, v in mapping.items() if k not in expected}
            if additional_values:
                lines = pprint.pformat(additional_values)
                additional = f"\n\nAdditional (non-matched) keys: \n{lines}"
            else:
                additional = ""
            self.fail(f"KV members were not a match. {diff}{additional}")


def run_module_doctest(
    mod_or_name,
    *,
    additional_globals: t.Optional[t.Dict[str, t.Any]] = None,
):
    """Run the doctests of the given module.

    All the symbols imported and/or defined in such module will be available to
    the doctests, additional symbols can be provided with `additional_globals`.

    All tests are run with NORMALIZE_WHITESPACE and ELLIPSIS.

    """
    from xotl.tools.names import nameof

    if isinstance(mod_or_name, str):
        module = importlib.import_module(mod_or_name)
        modname = mod_or_name
    else:
        module = mod_or_name
        modname = nameof(module, full=True, typed=False, inner=True)
    if not isinstance(module, ModuleType):
        raise ValueError(
            f"{mod_or_name} must be a module or fully qualified name to a module.  Got {module}."
        )
    with captured_stdout() as stdout, captured_stderr() as stderr:
        globs = dict(vars(module))
        if additional_globals:
            globs.update(additional_globals)
        failure_count, test_count = doctest.testmod(
            module,
            globs=globs,
            verbose=True,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            raise_on_error=False,
        )
    if test_count and failure_count:  # pragma: no cover
        print(stdout.getvalue())
        print(stderr.getvalue())
        raise AssertionError(f"{modname} doctest failed")
