#!usr/bin/env python
import sys

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

cmp_opcodes = {
    "IFEQ": "je",
    "IFNE": "jne",
    "IFLT": "jl",
    "IFLE": "jle",
    "IFGT": "jg",
    "IFGE": "jge"
}


class X86Generator():
    def __init__(self, il_program):
        """
        :type il_program: il.Program
        :param il_program: the generated IL program
        """
        # self.il_prog = il_program

        self.rodata = list()
        self.data = list()
        self.program = list()

        # list of dicts (register id -> offset in stack frame). Index in list is scope
        self.frame_locs = []

        # list of corresponding Functions
        self.frame_funcs = []

        self.init_program(il_program)

        self.asm_program(il_program)

    def init_program(self, il_prog):
        self.rodata.append("\t.section\t.rodata")
        self.data.append("\t.section\t.data")
        self.program.append("\t.section\t.text")

        for i in range(_get_max_scope(il_prog) + 1):
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

    def operand_value(self, operand):
        val_type = operand.operand_value.type

        if re.match("constant|string", val_type):
            return self.const_value(operand)
        elif val_type == "jump-target":
            return "{}".format(_convert_name_str(operand.operand_value.block))
        elif val_type == "native-target":
            return "{}".format(_convert_name_str(operand.operand_value.func))

    def const_value(self, operand):
        val_type = operand.operand_value.type

        if val_type == "int-constant":
            return "${}".format(operand.operand_value.value)
        elif val_type == "float-constant":
            pass
        elif val_type == "string":
            return self.string_value(operand.operand_value.value)

    def string_value(self, str_val):

        # make sure to check if this gives correct numbers
        name = ".string_{}".format(len(self.rodata) / 2)
        self.rodata.append(name + ":")
        self.rodata.append('\t.string \"{}\"'.format(str_val))
        return name

    def asm_program(self, prog):
        for func in prog.functions.itervalues():
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
            self.add_instr("movl $0, {}(%ebp)".format(_stack_offset(i)))

    def pop_stack_frame(self, func):
        self.add_instr("movl -4(%ebp), %ebx")
        self.add_instr("movl %ebx, display_{}".format(func.scope_level))
        self.add_instr("movl %ebp, %esp")
        self.add_instr("popl %ebp")
        self.add_instr("ret")

        self.frame_locs.pop()
        self.frame_funcs.pop()

    def asm_block(self, block):
        """
        :type block: il.BasicBlock
        :param block:
        :return:
        """

        self.program.append(_convert_name_str(block.name) + ":")
        for instr in block.instructions:
            self.asm_instruction(instr)


    def load(self, il_operand, asm_reg):
        oprnd_type = il_operand.operand_value.type

        if oprnd_type == "register":
            self.add_instr("movl {}, {}".format(self.access_location(il_operand), asm_reg))
        else:
            self.add_instr("movl {}, {}".format(self.operand_value(il_operand), asm_reg))

    def store(self, asm_reg, il_operand):
        self.add_instr("movl {}, {}".format(self.access_location(asm_reg), il_operand))

    def asm_instruction(self, instr):
        """
        :type instr: il.Instruction
        """

        if instr.op == "NOP":
            return self.asm_nop()
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
            return self.asm_exit()

    def asm_nop(self):
        self.add_instr("nop")

    def asm_imm(self, instr):
        sys.stderr.write(instr.A.operand_value.type)
        if re.match("target|string", instr.A.operand_value.type):
            self.add_instr("leal {}, {}".format(self.operand_value(instr.A), self.access_location(instr.R)))
        else:
            print "blah"
            self.add_instr("movl {}, {}".format(self.operand_value(instr.A), self.access_location(instr.R)))

    def asm_mv(self, instr):
        if instr.A.operand_value.type == "register":
            self.load(instr.A, "%eax")
            self.store("%eax", instr.R)
        else:
            self.add_instr("movl ${}, {}".format(self.operand_value(instr.A), self.access_location(instr.R)))

    def asm_add(self, instr):
        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("addl %ebx, %eax")
        self.store("%eax", instr.R)

    def asm_sub(self, instr):
        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("subl %ebx, %eax")
        self.store("%eax", instr.R)

    def asm_mul(self, instr):
        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("imull %ebx")
        self.store("%eax", instr.R)

    def asm_div(self, instr):
        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("movl $0, %edx")
        self.add_instr("idivl %ebx")
        self.store("%eax", instr.R)

    def asm_mod(self, instr):
        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("movl $0, %edx")
        self.add_instr("idivl %ebx")
        self.store("%edx", instr.R)

    def asm_jmp(self, instr):
        self.add_instr("jmp {}".format(self.operand_value(instr.A)))

    def asm_if(self, instr):
        opcode = cmp_opcodes[instr.op]

        self.load(instr.A, "%eax")
        self.load(instr.B, "%ebx")
        self.add_instr("compl %ebx %eax")
        self.add_instr("{} {}".format(opcode, self.operand_value(instr.R)))

    def asm_prm(self, instr):
        param_num = instr.A.operand_value.value
        offset = 4 * param_num + 8
        self.add_instr("movl {}(%ebp), %eax".format(offset))
        self.store("%eax", instr.R)

    def asm_call(self, instr):
        for arg_reg in reversed(instr.B.operand_value):
            reg_id, reg_scope = arg_reg.id, arg_reg.scope

            if reg_scope < self.frame_funcs[-1].scope_level:
                self.add_instr("movl display_{}, %esi".format(self.frame_funcs[-1].scope_level))
                loc = "{}(%esi)".format(_stack_offset(reg_id))
            else:
                loc = "{}(%ebp)".format(_stack_offset(reg_id))
            self.add_instr("pushl {}".format(loc))

        self.add_instr("call *{}".format(self.access_location(instr.A)))

        if instr.R.operand_type != "unit":
            self.store("%eax", instr.R)

        if len(instr.B.operand_value) > 0:
            self.add_instr("addl ${}, %esp".format(4*len(instr.B.operand_value)))

    def asm_rtrn(self, instr):
        self.load(instr.A, "%eax")
        self.pop_stack_frame(self.frame_funcs[-1])

    def asm_exit(self):
        self.add_instr("pushl $0")
        self.add_instr("call exit")



