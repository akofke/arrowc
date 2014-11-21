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
    def __init__(self):
        super(Function, self).__init__("function")
        self.name = ""
        self.func_type = None
        self.scope_level = None
        self.static_scope = None
        self.blocks = list()


class BasicBlock(ILType):
    def __init__(self):
        super(BasicBlock, self).__init__("block")
        self.name = ""
        self.next = list()
        self.prev = list()
        self.instructions = list()


class Instruction(ILType):
    def __init__(self, op):
        super(Instruction, self).__init__("instruction")
        self.op = op
        # operands A, B, R



class ArrowType(ILType):
    def __init__(self, arrow_type):
        super(ArrowType, self).__init__("arrow-type")

        if isinstance(arrow_type, arrowlang_types.Type):
            for attr, value in arrow_type.__dict__.iteritems():
                if attr == "params":
                    self.__setattr__("args", {
                        "components": self.make_components(value),
                        "name": "tuple",
                        "type": "arrow-type"
                    })
                else:
                    self.__setattr__(attr, value)
        else:
            print arrow_type

    def make_components(self, params_value):
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

    print json.dumps(ArrowType(arrowlang_types.library_funcs["print_int32"]), indent=4, default=json_convert)


if __name__ == '__main__':
    main()






