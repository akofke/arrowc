#!usr/bin/env python

import json
import arrowc.arrowlang_types as arrowlang_types


class ILType(object):
    def __init__(self, type_):
        self.type_ = type_


class Program(ILType):
    def __init__(self):
        super(Program, self).__init__("program")
        self.functions = list()
        self.types = dict()


class Function(ILType):
    def __init__(self, name, func_type, scope_level, static_scope):
        super(Function, self).__init__("function")
        self.name = name
        self.func_type = func_type
        self.scope_level = scope_level
        self.static_scope = static_scope
        self.blocks = list()


class BasicBlock(ILType):
    def __init__(self):
        super(BasicBlock, self).__init__("block")
        self.name = ""
        self.next = list()
        self.prev = list()
        self.instructions = list()

    def add_instr(self, instruction):
        self.instructions.append(instruction)


class Instruction(ILType):
    def __init__(self, op, A=Operand(), B=Operand(), R=Operand()):
        super(Instruction, self).__init__("instruction")
        self.op = op
        self.A = A
        self.B = B
        self.R = R



    def set_op(self, op, op_type, op_value):
        self.__getattribute__(op).operand_type = op_type
        self.__getattribute__(op).operand_value = op_value


class Operand(ILType):
    def __init__(self, ):
        super(Operand, self).__init__("operand")
        self.operand_value = {
            "type": "unit"
        }

        self.operand_type = "unit"



class Value(ILType):
    def __init__(self, type_, **kwargs):
        super(Value, self).__init__(type_)
        for key, val in kwargs.iteritems():
            self.__setattr__(key, val)


def int_const(value):
    return Value("int-constant", value=value)


def float_const(value):
    return Value("float-constant", value=value)


def register(scope, id_):
    return Value("register", scope=scope, id=id_)


def label(block, func):
    return Value("jump-target", block=block, func=func)


class ArrowType(ILType):
    def __init__(self, arrow_type):
        super(ArrowType, self).__init__("arrow-type")

        if isinstance(arrow_type, arrowlang_types.FuncType):
            func_dict = arrow_type.__dict__
            self.__setattr__("args", {
                "components": self.make_components(func_dict["params"]),
                "name": "tuple",
                "type": "arrow-type"
            })
            self.__setattr__("returns", ArrowType(func_dict["returns"]))
            self.__setattr__("name", "function")

        elif isinstance(arrow_type, arrowlang_types.Type):
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
        obj_dict["type"] = obj_dict.pop("type_")
        return obj_dict
    else:
        print il_obj
        raise TypeError


def main():
    prog = Program()
    func = Function()
    block = BasicBlock()
    instr = Instruction("IMM")

    block.instructions.append(instr)
    func.blocks.append(block)
    prog.functions.append(func)

    # print json.dumps(prog, indent=4, default=json_convert)

    print json.dumps(register(0, 1), indent=4, default=json_convert)


if __name__ == '__main__':
    main()






