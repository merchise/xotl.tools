from xotl.tools.future.textwrap import dedent


def test_textwrap_with_skip(snapshot):
    result = dedent(
        """Remove any common leading whitespace from every line in text.

        This can be used to make triple-quoted strings line up with the left edge of the display,
        while still presenting them in the source code in indented form.""",
        skip_firstline=True,
    )
    assert snapshot() == result


def test_textwrap_with_skip_one_line(snapshot):
    result = dedent(
        """Remove any common leading whitespace from every line in text.""",
        skip_firstline=True,
    )
    assert snapshot() == result
