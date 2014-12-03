#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types
import re
import json


def node_info(node):
    """
    0: Node label (e.g. Stmts, For, Decl, +, etc)
    1: Value if node has a value, otherwise type
    2: Type if node has a value

    :param node:
    :return: list of node components
    """
    return re.split(r",|:", node.children[0].label)

arith_ops = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD"
}


class ILGenerator():
    def __init__(self, typed_ast):
        self.ast = typed_ast
        self.reg_table = [dict()]
        self.func_param_table = dict()
        self.reg_counter = [0]

        self.program = Program()
        self.current_func = None
        self.current_block = None
        self.init_program()

    def get_json(self):
        pass

    def get_prettyprint(self):
        pass

    def get_register(self):
        """
        Gets the next free register in the current scope, and increments the register counter.
        :return: The next available register as a Register object
        """
        reg = Value.register(self.reg_counter[-1], len(self.reg_counter) - 1)
        self.reg_counter[-1] += 1
        return reg

    def get_param(self, func, param_num):
        pass

    def get_symbol_register(self, sym):
        for d in self.reg_table:
            if sym in d:
                return d[sym]


    # def write_instr(self, op, **operands):
    #     self.current_block.add_instr(op, **operands)

    def write_instr(self, instr):
        self.current_block.instructions.append(instr)

    def init_program(self):

        # add all arrowlang primitive types to program types list
        self.program.types.update((name, ArrowType(val)) for name, val in types.prims.iteritems())

        main_func = self.program.add_main()
        main_b0 = main_func.add_block()
        self.current_func = main_func
        self.current_block = main_b0

        for func_name, func_type in types.library_funcs.iteritems():
            a = Operand("label", Value.native_label(func_name))

            reg = self.get_register()
            r = Operand(str(func_type), reg)

            instr = Instruction("IMM", a=a, r=r)
            self.write_instr(instr)

            self.reg_table[-1].update({func_name: (reg, func_type)})

    def gen_il(self):
        for stmt in self.ast.children:


    def gen_stmt(self, node):
        node_type = node_info(node)[0]

        if re.match("Decl|ShortDecl", node_type):
            pass
        if re.match("")

    def gen_funcdef(self, node):
        func_name, func_type = node_info(node.children[0])[1:]



    def gen_call(self, node):
        sym_name = node_info(node.children[0])[1]


        for expr in node.children[1].children:
            instr = self.gen_expr(expr)
            expr_type = node_info(expr)[-1]
            instr.set_r(Operand(
                expr_type,
                self.get_register()
            ))






    def gen_decl(self, node):
        var_name, var_type = node_info(node)[1:]

        result_reg = self.get_register()
        r = Operand(var_type, result_reg)

        instr = self.gen_expr(node)
        instr.set_r(r)


    def gen_expr(self, node):
        node_type = node_info(node)[0]

        # +, -, *, /, or % operators
        if re.match("[+\-*/%]", node_type):
            pass
        elif re.match("int|float|string", node_type):
            instr = self.gen_literal(node.children[0])
            return instr
        elif node_type == "Symbol":
            pass
        elif node_type == "Call":
            pass
        elif node_type == "Cast":
            pass
        elif node_type == "Negate":
            pass

    def gen_literal(self, node):

        node_value, value_type = node_info(node)[1:]

        instr = Instruction(
            "IMM",
            a=Operand(value_type, node_value),
        )

        return instr

    def gen_arith_op(self, node, node_type):
        op = arith_ops[node_type]
        left_instr = self.gen_expr(node.children[0])
        right_instr = self.gen_expr(node.children[1])

        left_instr.set_r(self.get_register())
        right_instr.set_r(self.get_register())

        self.write_instr(left_instr)
        self.write_instr(right_instr)

        instr = Instruction(op, a=left_instr.R, b=right_instr.R)
        return instr








def main():
    il = ILGenerator()
    prog = il.program

    print json.dumps(prog, indent=4, default=json_convert)

if __name__ == '__main__':
    main()







