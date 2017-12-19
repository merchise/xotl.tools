- Fix encoding issues in `xoutil.string.cut_prefix`:func: and
  `xoutil.string.cut_suffix`:func:.

  Previously this code failed::

     >>> from xoutil.string import cut_prefix
     >>> cut_prefix(u'-\xe1', '-')
     Traceback ...
       ...
     UnicodeEncodeError: 'ascii' ...

  Now both functions force its second argument to be of the same type of the
  first.  See `xoutil.string.safe_decode`:func: and
  `xoutil.string.safe_encode`:func:.
