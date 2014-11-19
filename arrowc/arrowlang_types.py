class Type:
    """
    Base Type class. All Arrowlang types have a name so this class only has a name field.
    """

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if type(other) is type(self):
            return other.name == self.name
        else:
            return False

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class SizedType(Type):
    """
    Type that has only a name and a size.
    """

    def __init__(self, name, size):
        Type.__init__(self, name)
        self.size = size

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.size == other.size
        else:
            return False


class IntType(Type):
    """
    Sized int types that can be signed or unsigned.
    """

    def __init__(self, name, size, signed):
        Type.__init__(self, name)
        self.size = size
        self.signed = signed

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.size == other.size and self.signed == other.signed
        else:
            return False


class FuncType(Type):
    """
    Function type that has a list of types as params and a single return type.
    """

    def __init__(self, params, return_type):
        Type.__init__(self, "fn({})->{!s}".format(', '.join(map(str, params)), return_type))
        self.params = params
        self.return_type = return_type

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name \
                and tuple(self.params) == tuple(other.params) and self.return_type == other.return_type
        else:
            return False
