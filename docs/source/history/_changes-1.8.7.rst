- Add parameter 'encoding' to ``xoutil.string.slugify`` and
  ``xoutil.eight.string.force_ascii``.  (bug #25).

- Stop using `locale.getpreferredencoding`:func: in
  ``xoutil.future.codecs.force_encoding``.  Also related to bug #25.
