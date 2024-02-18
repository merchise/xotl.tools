from xotl.tools.objects import classproperty, copy_class


class Foo:
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @classproperty
    def class_name(cls):
        return cls.get_name()


def check_str(s: str) -> str:
    return s


def check_foo(f: Foo) -> Foo:
    return f


if __name__ == "__main__":
    foo = Foo()
    check_str(foo.class_name)

    Foo2 = copy_class(Foo, new_name="Foo2")
    foo2 = Foo2()
    check_foo(foo2)
    check_str(foo2.class_name)
