#!usr/bin/env python

import arrowc.arrowlang_il.il_types
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


class X86Generator():
    def __init__(self, il_program):
        """
        :type il_program: il_types.Program
        :param il_program: the generated IL program
        """

        self.rodata = list()
        self.data = list()
        self.program = list()

        self.init_program()

    def init_program(self):
        self.rodata.append("\t.section\t.rodata")
        self.data.append("\t.section\t.data")
        self.program.append("\t.section\t.text")

    def get_program(self):
        native_code = read_native()
        return "\n\n".join((
            "".join(line for line in native_code),
            "\n".join(line for line in self.rodata),
            "\n".join(line for line in self.data),
            "\n".join(line for line in self.program)
        ))



