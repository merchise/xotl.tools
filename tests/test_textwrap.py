# -*- encoding: utf-8 -*-

# Most of the code was taken from the Python 3.3 code base.
#
# Copyright (c) 2001-2012 Python Software Foundation.  All rights reserved.
#

import unittest
from xotl.tools.future.textwrap import wrap, fill, dedent, indent


class BaseTestCase(unittest.TestCase):
    """Parent class with utility methods for textwrap tests."""

    def show(self, textin):
        if isinstance(textin, list):
            result = []
            for i in range(len(textin)):
                result.append("  %d: %r" % (i, textin[i]))
            result = "\n".join(result)
        elif isinstance(textin, str):
            result = "  %s\n" % repr(textin)
        return result

    def check(self, result, expect):
        msg = "expected:\n%s\nbut got:\n%s" % (self.show(expect), self.show(result))
        self.assertEqual(result, expect, msg)

    def check_wrap(self, text, width, expect, **kwargs):
        result = wrap(text, width, **kwargs)
        self.check(result, expect)

    def check_split(self, text, expect):
        result = self.wrapper._split(text)
        self.assertEqual(
            result, expect, "\nexpected %r\n" "but got  %r" % (expect, result)
        )


class IndentTestCases(BaseTestCase):

    # called before each test method
    def setUp(self):
        self.text = """\
This paragraph will be filled, first without any indentation,
and then with some (including a hanging indent)."""

    def test_fill(self):
        # Test the fill() method

        expect = """\
This paragraph will be filled, first
without any indentation, and then with
some (including a hanging indent)."""

        result = fill(self.text, 40)
        self.check(result, expect)

    def test_initial_indent(self):
        # Test initial_indent parameter

        expect = [
            "     This paragraph will be filled,",
            "first without any indentation, and then",
            "with some (including a hanging indent).",
        ]
        result = wrap(self.text, 40, initial_indent="     ")
        self.check(result, expect)

        expect = "\n".join(expect)
        result = fill(self.text, 40, initial_indent="     ")
        self.check(result, expect)

    def test_subsequent_indent(self):
        # Test subsequent_indent parameter
        expect = """\
  * This paragraph will be filled, first
    without any indentation, and then
    with some (including a hanging
    indent)."""

        result = fill(self.text, 40, initial_indent="  * ", subsequent_indent="    ")
        self.check(result, expect)


# Despite the similar names, DedentTestCase is *not* the inverse
# of IndentTestCase!
class DedentTestCase(unittest.TestCase):
    def assertUnchanged(self, text):
        """assert that dedent() has no effect on 'text'"""
        self.assertEqual(text, dedent(text))

    def test_dedent_nomargin(self):
        # No lines indented.
        text = "Hello there.\nHow are you?\nOh good, I'm glad."
        self.assertUnchanged(text)

        # Similar, with a blank line.
        text = "Hello there.\n\nBoo!"
        self.assertUnchanged(text)

        # Some lines indented, but overall margin is still zero.
        text = "Hello there.\n  This is indented."
        self.assertUnchanged(text)

        # Again, add a blank line.
        text = "Hello there.\n\n  Boo!\n"
        self.assertUnchanged(text)

    def test_dedent_even(self):
        # All lines indented by two spaces.
        text = "  Hello there.\n  How are ya?\n  Oh good."
        expect = "Hello there.\nHow are ya?\nOh good."
        self.assertEqual(expect, dedent(text))

        # Same, with blank lines.
        text = "  Hello there.\n\n  How are ya?\n  Oh good.\n"
        expect = "Hello there.\n\nHow are ya?\nOh good.\n"
        self.assertEqual(expect, dedent(text))

        # Now indent one of the blank lines.
        text = "  Hello there.\n  \n  How are ya?\n  Oh good.\n"
        expect = "Hello there.\n\nHow are ya?\nOh good.\n"
        self.assertEqual(expect, dedent(text))

    def test_dedent_uneven(self):
        # Lines indented unevenly.
        text = """\
        def foo():
            while 1:
                return foo
        """
        expect = """\
def foo():
    while 1:
        return foo
"""
        self.assertEqual(expect, dedent(text))

        # Uneven indentation with a blank line.
        text = "  Foo\n    Bar\n\n   Baz\n"
        expect = "Foo\n  Bar\n\n Baz\n"
        self.assertEqual(expect, dedent(text))

        # Uneven indentation with a whitespace-only line.
        text = "  Foo\n    Bar\n \n   Baz\n"
        expect = "Foo\n  Bar\n\n Baz\n"
        self.assertEqual(expect, dedent(text))

    # dedent() should not mangle internal tabs
    def test_dedent_preserve_internal_tabs(self):
        text = "  hello\tthere\n  how are\tyou?"
        expect = "hello\tthere\nhow are\tyou?"
        self.assertEqual(expect, dedent(text))

        # make sure that it preserves tabs when it's not making any
        # changes at all
        self.assertEqual(expect, dedent(expect))

    # dedent() should not mangle tabs in the margin (i.e.
    # tabs and spaces both count as margin, but are *not*
    # considered equivalent)
    def test_dedent_preserve_margin_tabs(self):
        text = "  hello there\n\thow are you?"
        self.assertUnchanged(text)

        # same effect even if we have 8 spaces
        text = "        hello there\n\thow are you?"
        self.assertUnchanged(text)

        # dedent() only removes whitespace that can be uniformly removed!
        text = "\thello there\n\thow are you?"
        expect = "hello there\nhow are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \thello there\n  \thow are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \t  hello there\n  \t  how are you?"
        self.assertEqual(expect, dedent(text))

        text = "  \thello there\n  \t  how are you?"
        expect = "hello there\n  how are you?"
        self.assertEqual(expect, dedent(text))


# Test textwrap.indent
class IndentTestCase(unittest.TestCase):
    # The examples used for tests. If any of these change, the expected
    # results in the various test cases must also be updated.
    # The roundtrip cases are separate, because textwrap.dedent doesn't
    # handle Windows line endings
    ROUNDTRIP_CASES = (
        # Basic test case
        "Hi.\nThis is a test.\nTesting.",
        # Include a blank line
        "Hi.\nThis is a test.\n\nTesting.",
        # Include leading and trailing blank lines
        "\nHi.\nThis is a test.\nTesting.\n",
    )
    CASES = ROUNDTRIP_CASES + (
        # Use Windows line endings
        "Hi.\r\nThis is a test.\r\nTesting.\r\n",
        # Pathological case
        "\nHi.\r\nThis is a test.\n\r\nTesting.\r\n\n",
    )

    def test_indent_nomargin_default(self):
        # indent should do nothing if 'prefix' is empty.
        for text in self.CASES:
            self.assertEqual(indent(text, ""), text)

    def test_indent_nomargin_explicit_default(self):
        # The same as test_indent_nomargin, but explicitly requesting
        # the default behaviour by passing None as the predicate
        for text in self.CASES:
            self.assertEqual(indent(text, "", None), text)

    def test_indent_nomargin_all_lines(self):
        # The same as test_indent_nomargin, but using the optional
        # predicate argument
        predicate = lambda line: True
        for text in self.CASES:
            self.assertEqual(indent(text, "", predicate), text)

    def test_indent_no_lines(self):
        # Explicitly skip indenting any lines
        predicate = lambda line: False
        for text in self.CASES:
            self.assertEqual(indent(text, "    ", predicate), text)

    def test_roundtrip_spaces(self):
        # A whitespace prefix should roundtrip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, "    ")), text)

    def test_roundtrip_tabs(self):
        # A whitespace prefix should roundtrip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, "\t\t")), text)

    def test_roundtrip_mixed(self):
        # A whitespace prefix should roundtrip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(indent(text, " \t  \t ")), text)

    def test_indent_default(self):
        # Test default indenting of lines that are not whitespace only
        prefix = "  "
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n\n  Testing.",
            # Include leading and trailing blank lines
            "\n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "\n  Hi.\r\n  This is a test.\n\r\n  Testing.\r\n\n",
        )
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix), expect)

    def test_indent_explicit_default(self):
        # Test default indenting of lines that are not whitespace only
        prefix = "  "
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n\n  Testing.",
            # Include leading and trailing blank lines
            "\n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "\n  Hi.\r\n  This is a test.\n\r\n  Testing.\r\n\n",
        )
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, None), expect)

    def test_indent_all_lines(self):
        # Add 'prefix' to all lines, including whitespace-only ones.
        prefix = "  "
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n  \n  Testing.",
            # Include leading and trailing blank lines
            "  \n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "  \n  Hi.\r\n  This is a test.\n  \r\n  Testing.\r\n  \n",
        )
        predicate = lambda line: True
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, predicate), expect)

    def test_indent_empty_lines(self):
        # Add 'prefix' solely to whitespace-only lines.
        prefix = "  "
        expected = (
            # Basic test case
            "Hi.\nThis is a test.\nTesting.",
            # Include a blank line
            "Hi.\nThis is a test.\n  \nTesting.",
            # Include leading and trailing blank lines
            "  \nHi.\nThis is a test.\nTesting.\n",
            # Use Windows line endings
            "Hi.\r\nThis is a test.\r\nTesting.\r\n",
            # Pathological case
            "  \nHi.\r\nThis is a test.\n  \r\nTesting.\r\n  \n",
        )
        predicate = lambda line: not line.strip()
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(indent(text, prefix, predicate), expect)
