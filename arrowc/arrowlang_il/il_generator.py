#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types


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

    




def main():
    il = ILGenerator()
    prog = il.program

    print json.dumps(prog, indent=4, default=json_convert)

if __name__ == '__main__':
    main()







