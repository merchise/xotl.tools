Differences between Python 2 and 3 of standard `inspect`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Python 2.x and until version 3.2 is missing the function
`~inspect.getattr_static`:func: and some internal dependencies.

We implemented them in `xoutil.eight.inspect`:mod: module, but there is some
problems:

- Instances of `GetSetDescriptorType` list `__objclass__` as part of is
  attributes when `dir` is executed, but accessing it in `PyPy` raises and
  `AttributeError`.

- In `PyPy` ``MemberDescriptorType is GetSetDescriptorType`` is True, because
  of that `MemberDescriptorType` is fixed in `xoutil` to its proper
  definition.  Nevertheless, this is not related to reported problem, but is
  mentioned because Manu implemented that before with a class, if I remember
  well.

- In our implementation we care about old style classes (OSC) in some context
  where maybe is not needed, for example using descriptors: in OSC descriptors
  fail to assign values (method `__set__` is not used).  Maybe is time to
  deprecate use of OSC in `xoutil.eight`.
