- Introduces :class:`xoutil.collections.OpenDictMixin` and
  :class:`xoutil.collections.StackedDict`.

- Makes :class:`execution context <xoutil.context.Context>` inherit from
  :class:`xoutil.collections.StackedDict`.

  Whenever you enter a context a new level is :meth:`pushed
  <xoutil.collections.StackedDict.push>`, when you leave the context a level is
  :meth:`poped <xoutil.collections.StackedDict.pop>`.
