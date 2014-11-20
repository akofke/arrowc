#!usr/bin/env python

import json

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
    def __init__(self):
        super(ArrowType, self).__init__("arrow-type")


def json_convert(il_obj):
    if isinstance(il_obj, ILType):
        obj_dict = il_obj.__dict__
        obj_dict["type"] = obj_dict.pop("type_")
        return obj_dict
    else:
        raise TypeError


def main():
    prog = Program()
    func = Function()
    block = BasicBlock()
    instr = Instruction("IMM")

    block.instructions.append(instr)
    func.blocks.append(block)
    prog.functions.append(func)

    print json.dumps(prog, indent=4, default=json_convert)

if __name__ == '__main__':
    main()






