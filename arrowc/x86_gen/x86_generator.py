#!usr/bin/env python

import arrowc.arrowlang_il.il_types as il
import os
import re


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

def _convert_name_str(name):
    """
    :type name: str
    """
    return name.replace("-", "_")


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

        self.frame_locs = [dict()]

        self.init_program()

    def init_program(self):
        self.rodata.append("\t.section\t.rodata")
        self.data.append("\t.section\t.data")
        self.program.append("\t.section\t.text")

        for i in range(_get_max_scope(self.il_prog) + 1):
            self.data.append("display_{}:".format(i))
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

    def asm_program(self, prog):
        for func in prog.functions:
            self.asm_function(func)

    def access_location(self, operand):
        """
        :type operand: il.Operand
        """

        reg = operand.operand_value.

    def asm_function(self, func):
        converted_name = _convert_name_str(func.name)

        self.program.append("")
        self.program.append("\t.global {}".format(converted_name))
        self.program.append("\t.type {} @function".format(converted_name))
        self.program.append("{}:".format(converted_name))

    def push_stack_frame(self, func):

        self.add_instr("pushl %ebp")
        self.add_instr("movl %esp, %ebp")



    def instructions(self, instr):
        """
        :type instr: il.Instruction
        """

        if instr.op == "NOP":
            return self.asm_nop(instr)
        elif instr.op == "IMM":
            return self.asm_imm(instr)
        elif instr.op == "MV":
            return self.asm_mv(instr)
        elif instr.op == "ADD":
            return self.asm_add(instr)
        elif instr.op == "SUB":
            return self.asm_sub(instr)
        elif instr.op == "MUL":
            return self.asm_mul(instr)
        elif instr.op == "DIV":
            return self.asm_div(instr)
        elif instr.op == "MOD":
            return self.asm_mod(instr)
        elif instr.op == "J":
            return self.asm_jmp(instr)
        elif re.match("IFEQ|IFNE|IFLT|IFLE|IFGT|IFGE", instr.op):
            return self.asm_if(instr)
        elif instr.op == "PRM":
            return self.asm_prm(instr)
        elif instr.op == "CALL":
            return self.asm_call(instr)
        elif instr.op == "RTRN":
            return self.asm_rtrn(instr)
        elif instr.op == "EXIT":
            return self.asm_exit(instr)

    def asm_nop(self, instr):
        pass

    def asm_imm(self, instr):
        self.program.append("movl ${}, ")

    def asm_mv(self, instr):
        pass

    def asm_add(self, instr):
        pass

    def asm_sub(self, instr):
        pass

    def asm_mul(self, instr):
        pass

    def asm_div(self, instr):
        pass

    def asm_mod(self, instr):
        pass

    def asm_jmp(self, instr):
        pass

    def asm_if(self, instr):
        pass

    def asm_prm(self, instr):
        pass

    def asm_call(self, instr):
        pass

    def asm_rtrn(self, instr):
        pass

    def asm_exit(self, instr):
        pass



