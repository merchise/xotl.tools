- Loads of improvements for Python 3k compatibility: Several modules were
  fixed or adapted to work on both Python 2.7 and Python 3.2. They include (but
  we might have forgotten some):

  - `xoutil.context`:mod:.
  - `!xoutil.aop.basic`:mod:.
  - `xoutil.deprecation`:mod:.
  - `!xoutil.proxy`:mod:.

- Rescued `xoutil.annotate`:mod: and is going to be supported from
  now on.

- Introduced module `xoutil.subprocess`:mod: and function
  `xoutil.subprocess.call_and_check_output`:func:.

- Introduced module `xoutil.decorator.compat`:mod: that enables constructions
  that are interoperable in Python 2 and Python 3.

- Introduced `xoutil.iterators.zip`:func:, `xoutil.iterators.izip`:func:,
  `xoutil.iterators.map`:func:, and `xoutil.iterators.imap`:func:.


..  LocalWords:  xoutil
