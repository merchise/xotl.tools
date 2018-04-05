- Make `~xoutil.future.datetime.TimeSpan`:class: intersection *inversible*.
  Before, doing ``date.today() & TimeSpan()`` raised a TypeError, but
  swapping the operands worked.  Now, both ways work.
