- This is the first release for which Python 2 no longer supported.  It was a
  good time!  Good bye, Python 2!

- The following imports are no longer available.  Look for them in
  `xoutil.future`:mod:\ :

  .. hlist::
     :columns: 3

     - ``xoutil.collection``
     - ``xoutil.datetime``
     - ``xoutil.functools``
     - ``xoutil.inspect``
     - ``xoutil.iterators``
     - ``xoutil.json``
     - ``xoutil.pprint``
     - ``xoutil.subprocess``
     - ``xoutil.textwrap``
     - ``xoutil.threading``
     - ``xoutil.types``

- Deprecate modules that only provided a unifying mechanism between Python 2
  and 3, or that backported features from Python 3 to Python 2:

  .. hlist::
     :columns: 3

     - ``xoutil.annotate``
     - ``xoutil.eight``
     - ``xoutil.eight.urllib``

- Remove deprecated module ``xoutil.html``.
