- Fix encoding issues in ``xoutil.string.cut_prefix`` and
  ``xoutil.string.cut_suffix``.

  Previously this code failed::

     >>> from xoutil.string import cut_prefix
     >>> cut_prefix(u'-\xe1', '-')
     Traceback ...
       ...
     UnicodeEncodeError: 'ascii' ...

  Now both functions force its second argument to be of the same type of the
  first.  See ``xoutil.string.safe_decode`` and
  ``xoutil.string.safe_encode``.
