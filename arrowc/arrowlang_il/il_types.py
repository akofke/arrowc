#!usr/bin/env python

import json
import arrowc.arrowlang_types as al_types


class ILType(object):
    """
    General object used to represent intermediate language types.
    All IL json type objects have a type field. An underscore is used to not shadow the python type builtin.
    """

    def __init__(self, type_):
        self.type = type_


class Program(ILType):
    """
    Program types have a list of functions and a list of types
    """

    def __init__(self):
        super(Program, self).__init__("program")
        self.functions = dict()
        self.types = dict()

    def add_main(self):
        main_type = al_types.FuncType([], al_types.prims["unit"])
        m = Function("main", main_type, 0)
        self.functions.update({m.name: m})
        self.add_type(main_type)
        return m

    def add_func(self, func_name, func_type, scope_level, static_scope):
        f = Function("fn-{}-{}".format(len(self.functions) - 1, func_name), func_type, scope_level, static_scope)
        self.functions.update({f.name: f})
        self.add_type(func_type)
        return f

    def add_type(self, arrow_type):
        self.types.update({str(arrow_type): ArrowType(arrow_type)})




class Function(ILType):
    """
    Functions have a name, function type, scope level (main starts at 0), static scope (a list of containing functions),
    and a list of blocks.
    """

    def __init__(self, func_name, func_type, scope_level, static_scope=list()):
        super(Function, self).__init__("function")
        self.name = func_name
        self.func_type = str(func_type)
        self.scope_level = scope_level
        self.static_scope = static_scope
        self.blocks = list()

    def add_block(self):
        block = BasicBlock("{}-b-{}".format(self.name, len(self.blocks)))
        self.blocks.append(block)
        return block




class BasicBlock(ILType):
    """
    Blocks have a name, lists of next and previous blocks, and a list of instructions.
    """

    def __init__(self, name):
        super(BasicBlock, self).__init__("block")
        self.name = name
        self.next = list()
        self.prev = list()
        self.instructions = list()

    def add_instr(self, op, **kwargs):
        self.instructions.append(Instruction(op, **kwargs))





class Operand(ILType):
    """
    Operands have the following fields:

    operand_value: a Value object (can be a register, label, literal, etc)
    operand_type: the type of the operand; i.e. label if the value is a jump target or native target,
    the type contained in the register if the value is a register, or the type of the literal if the value
    is a literal

    Operands that are blank have the default unit type.
    """

    def __init__(self, op_type="unit", op_val=None):
        super(Operand, self).__init__("operand")

        if not op_val:
            op_val = {'type': "unit"}
        self.operand_type = str(op_type)
        self.operand_value = op_val


class Instruction(ILType):
    """
    Instructions contain the name of the operation, and operands A (first argument), B (second argument),
    and R (register to put result)
    """

    def __init__(self, op, a=Operand(), b=Operand(), r=Operand()):
        super(Instruction, self).__init__("instruction")
        self.op = op
        self.A = a
        self.B = b
        self.R = r

    def set_a(self, operand):
        self.A = operand

    def set_b(self, operand):
        self.B = operand

    def set_r(self, operand):
        self.R = operand


class Value(ILType):
    """

    """

    def __init__(self, type_, **kwargs):
        super(Value, self).__init__(type_)
        for key, val in kwargs.iteritems():
            self.__setattr__(key, val)

    @staticmethod
    def int_const(value):
        return Value("int-constant", value=int(value))

    @staticmethod
    def float_const(value):
        return Value("float-constant", value=float(value))

    @staticmethod
    def register(id_, scope):
        return Value("register", id=id_, scope=scope)

    @staticmethod
    def jmp_label(block, func):
        return Value("jump-target", block=block, func=func)

    @staticmethod
    def native_label(func_name):
        return Value("native-target", func=func_name)


    @staticmethod
    def const(const_type, value):
        if const_type.name.startswith("int"):
            return Value("int-constant", value=value)
        elif const_type.name.startswith("float"):
            return Value("float-constant", value=value)
        elif const_type.name == "string":
            return Value("string", value=value)


class ArrowType(ILType):
    def __init__(self, arrow_type):
        super(ArrowType, self).__init__("arrow-type")

        if isinstance(arrow_type, al_types.FuncType):
            func_dict = arrow_type.__dict__
            self.__setattr__("args", {
                "components": self.make_components(func_dict["params"]),
                "name": "tuple",
                "type": "arrow-type"
            })
            self.__setattr__("returns", ArrowType(func_dict["returns"]))
            self.__setattr__("name", "function")

        elif isinstance(arrow_type, al_types.Type):
            for attr, value in arrow_type.__dict__.iteritems():
                self.__setattr__(attr, value)
        else:
            print arrow_type

    @staticmethod
    def make_components(params_value):
        if len(params_value) == 0:
            return None
        else:
            return tuple(ArrowType(arg) for arg in params_value)


def json_convert(il_obj):
    if isinstance(il_obj, ILType):
        obj_dict = il_obj.__dict__
        # obj_dict["type"] = obj_dict.pop("type_")

        # remove private fields not used for json
        # for key in obj_dict.keys():
        #     if key.startswith("_"):
        #         obj_dict.pop(key)

        return obj_dict



def main():
    prog = Program()
    # func = Function()
    # block = BasicBlock()
    # instr = Instruction("IMM")

    # print json.dumps(prog, indent=4, default=json_convert)

    print json.dumps(prog, indent=4, default=json_convert)


if __name__ == '__main__':
    main()






