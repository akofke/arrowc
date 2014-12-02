#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types
import re


def node_info(node):
    return re.split(r",|:", node.children[0].label)


class ILGenerator():
    def __init__(self):
        self.reg_table = [dict()]
        self.reg_counter = [0]

        self.program = Program()
        self.init_program()

    def get_register(self):
        """

        :return:
        """
        reg = Value.register(len(self.reg_counter) - 1, self.reg_counter[-1])
        self.reg_counter[-1] += 1
        return reg

    def init_program(self):

        # add all arrowlang primitive types to program types list
        self.program.types.update((name, ArrowType(val)) for name, val in types.prims.iteritems())

        main_func = self.program.add_main()
        main_b0 = main_func.add_block()

        for func_name, func_type in types.library_funcs.iteritems():
            a = Operand("label", Value.native_label(func_name))

            reg = self.get_register()
            r = Operand(str(func_type), reg)

            main_b0.add_instr("IMM", a=a, r=r)

            self.reg_table[-1].update({func_name: (reg, func_type)})

    def gen_decl(self, node):
        var_name, var_type = node_info(node)[1:]

        result_reg = self.get_register()
        r = Operand(var_type, result_reg)


    def gen_expr(self):




def main():
    il = ILGenerator()
    prog = il.program

    print json.dumps(prog, indent=4, default=json_convert)

if __name__ == '__main__':
    main()







