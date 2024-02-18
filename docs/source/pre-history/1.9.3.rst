- Make ``xoutil.future.datetime.TimeSpan`` intersection *inversible*.
  Before, doing ``date.today() & TimeSpan()`` raised a TypeError, but
  swapping the operands worked.  Now, both ways work.

- Add ``xoutil.objects.delegator`` and
  ``xoutil.objects.DelegatedAttribute``.
