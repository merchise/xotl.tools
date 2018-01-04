- Add parameter 'encoding' to `~xoutil.string.slugify`:func: and
  `~xoutil.eight.string.force_ascii`:func:.  This solves bug `#25`_.

- Stop using `locale.getpreferredencoding`:func: in
  `~xoutil.future.codecs.force_encoding`:func:.  Also related to bug `#25`_.

.. _#25: https://gitlab.lahavane.com/merchise/xoutil/issues/25
