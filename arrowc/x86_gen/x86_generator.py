#!usr/bin/env python

import arrowc.arrowlang_il.il_types as il
import os


def gen_x86(il_program):
    generator = X86Generator(il_program)
    return generator.get_program()


def read_native():
    try:
        with open(os.path.join("arrowc", "x86_gen", "native", "native.s")) as native:
            return native.readlines()
    except IOError, e:
        raise e


def _get_max_scope(prog):
    """
    :type prog: il.Program
    """

    return max(function.scope_level for function in prog.functions.itervalues())


class X86Generator():
    def __init__(self, il_program):
        """
        :type il_program: il.Program
        :param il_program: the generated IL program
        """
        self.il_prog = il_program

        self.rodata = list()
        self.data = list()
        self.program = list()

        self.init_program()

    def init_program(self):
        self.rodata.append("\t.section\t.rodata")
        self.data.append("\t.section\t.data")
        self.program.append("\t.section\t.text")

        for i in range(_get_max_scope(self.il_prog) + 1):
            self.data.append("display_{}".format(i))
            self.data.append("\t.long 0")





    def get_program(self):
        native_code = read_native()
        return "\n\n".join((
            "".join(line for line in native_code),
            "\n".join(line for line in self.rodata),
            "\n".join(line for line in self.data),
            "\n".join(line for line in self.program)
        ))

    def add_instr(self, instr):
        self.program.append("\t{}".format(instr))



