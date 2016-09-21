Special characters in a wild-carded name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:date: 2016-09-21

Python `fnmatch`:mod: standard module lack of some processing in
`~fnmatch.translate`:func:\: alternation of comma-separated alternatives;
thus, ``foo{bar,lish}`` would be read as ``foobar`` or ``foolish``.

In ``xtash.bag.glob.py`` there is an initial implementation for that.
