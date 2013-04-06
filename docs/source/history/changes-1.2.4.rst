- Makes execution context's data stacked.

  When passing data to a :class:`xoutil.context.Context` and entering, each
  level of data does not overwrite upper levels but simply supersedes: when the
  context is exited the upper level data remains the same.

  Also you may access the keys of the `data` directly with the "dot" notation
  like an opendict::

     c1 = 'CONTEXT-1'
     with context(c1, a=1, b=1) as cc1:
	 with context(c1, a=2) as cc2:
	     assert cc2 is cc1
	     assert cc2.data.a == 2
	     assert cc2.data.b == 1 # Given by the upper enclosing level

	     # Let's change it for this level
	     cc2.data.b = 'jailed!'
	     assert cc2.data.b == 'jailed!'

	 # But in the upper level both a and b stay the same and you can test
	 # it with [key]
	 assert cc1.data['a'] == 1
	 assert cc1.data['b'] == 1
