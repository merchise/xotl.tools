from xotl.tools.objects import classproperty


class Foo:
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @classproperty
    def class_name(cls):
        return cls.get_name()


def check_str(s: str) -> str:
    return s


if __name__ == "__main__":
    foo = Foo()
    check_str(foo.class_name)
