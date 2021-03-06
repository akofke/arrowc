

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
        self.returns = return_type

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name \
                and tuple(self.params) == tuple(other.params) and self.returns == other.return_type
        else:
            return False

class TupleType(Type):
    def __init__(self, comps):
        Type.__init__(self, tuple)
        self.components = tuple(ar_type for ar_type in comps)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.components == other.components
        else:
            return False

    def __str__(self):
        return "({})".format(", ".join(map(str, self.components)))


prims = {
    "unit": Type("unit"),
    "boolean": SizedType("boolean", 1),
    "int32": IntType("int32", 32, True),
    "uint32": IntType("uint32", 32, False),
    "int8": IntType("int8", 8, True),
    "uint8": IntType("uint8", 8, False),
    "float32": SizedType("float32", 32),
    "string": Type("string")
}

library_funcs = {
    "print_int32": FuncType((prims["int32"],), prims["unit"]),
    "print_uint32": FuncType((prims["uint32"],), prims["unit"]),
    "print_int8": FuncType((prims["int8"],), prims["unit"]),
    "print_uint8": FuncType((prims["uint8"],), prims["unit"]),
    "print_float32": FuncType((prims["float32"],), prims["unit"]),
    "print": FuncType((prims["string"],), prims["unit"])
}

if __name__ == '__main__':
    print TupleType([prim for prim in prims.itervalues()])