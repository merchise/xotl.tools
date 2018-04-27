- Add parameter 'encoding' to `~xoutil.string.slugify`:func: and
  `~xoutil.eight.string.force_ascii`:func:.  (bug #25).

- Stop using `locale.getpreferredencoding`:func: in
  `~xoutil.future.codecs.force_encoding`:func:.  Also related to bug #25.
