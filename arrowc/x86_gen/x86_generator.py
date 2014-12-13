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

def _stack_offset(i):
    """
    :type i: int
    :param i: the id of a register
    :return: the stack offset of a register with id i
    """
    return -4 * i - 8


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

        # list of dicts (register id -> offset in stack frame). Index in list is scope
        self.frame_locs = []

        # list of corresponding Functions
        self.frame_funcs = []

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

    def access_location(self, operand):
        """
        :type operand: il.Operand
        :rtype: str
        """

        reg_id, reg_scope = operand.operand_value.id, operand.operand_value.scope

        if reg_scope < self.frame_funcs[-1].scope_level:
            self.add_instr("movl display_{}, %esi".format(self.frame_funcs[-1].scope_level))
            return "{}(%esi)".format(_stack_offset(reg_id))
        else:
            return "{}(%ebp)".format(_stack_offset(reg_id))

    def asm_program(self, prog):
        for func in prog.functions:
            self.asm_function(func)

    def asm_function(self, func):
        converted_name = _convert_name_str(func.name)

        self.program.append("")
        self.program.append("\t.global {}".format(converted_name))
        self.program.append("\t.type {} @function".format(converted_name))
        self.program.append("{}:".format(converted_name))

        self.push_stack_frame(func)
        for block in func.blocks:
            self.asm_block(block)

    def push_stack_frame(self, func):
        self.frame_funcs.append(func)
        self.frame_locs.append(dict())

        self.add_instr("pushl %ebp")
        self.add_instr("movl %esp, %ebp")
        self.add_instr("pushl display_{}".format(func.scope_level))
        self.add_instr("subl ${}, %esp".format(func.reg_count_ * 4))

        for i in range(func.reg_count_):
            self.frame_locs[-1][i] = _stack_offset(i)

    def pop_stack_frame(self, func):
        self.add_instr("movl -4(%ebp), %ebx")
        self.add_instr("movl %ebx, display_{}".format(func.scope_level))
        self.add_instr("movl %ebp, %esp")
        self.add_instr("popl %ebp")
        self.add_instr("ret")

    def asm_block(self, block):
        """
        :type block: il.BasicBlock
        :param block:
        :return:
        """

        for instr in block.instructions:
            self.asm_instruction(instr)

    def asm_instruction(self, instr):
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



