============================================================================
:mod:`xoutil.html.parser` -- A simple parser that can handle HTML and XHTML.
============================================================================

.. module:: xoutil.html.parser

This module defines a class HTMLParser which serves as the basis for parsing
text files formatted in HTML (HyperText Mark-up Language) and XHTML.

.. warning:: This module has not being made Python 2.7 and 3.2 compatible.

.. class:: HTMLParser(strict=True)

   Create a parser instance. If strict is True (the default), invalid HTML
   results in :class:`HTMLParseError` exceptions [1]. If strict is False, the
   parser uses heuristics to make a best guess at the intention of any invalid
   HTML it encounters, similar to the way most browsers do. Using strict=False
   is advised.

   An :class`HTMLParser` instance is fed HTML data and calls handler methods
   when start tags, end tags, text, comments, and other markup elements are
   encountered. The user should subclass HTMLParser and override its methods to
   implement the desired behavior.

   This parser does not check that end tags match start tags or call the
   end-tag handler for elements which are closed implicitly by closing an outer
   element.

   .. versionchanged:: 3.2 strict keyword added

.. class:: HTMLParseError

   Exception raised by the :class:`HTMLParser` class when it encounters an
   error while parsing and strict is True. This exception provides three
   attributes: msg is a brief message explaining the error, lineno is the
   number of the line on which the broken construct was detected, and offset is
   the number of characters into the line at which the construct starts.
