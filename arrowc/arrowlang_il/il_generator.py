#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types
import re
import json


def node_label(node):
    """
    Gets the type of the node itself, i.e. "Stmts", "If", "Int", "Symbol", etc
    """
    return re.split(",|:", node.label)[0]

def node_data(node):
    return re.split(",|:", node.label)[1]

# def node_value(node):
#     return node_data(node)


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

        # maps symbols to Operands, i.e. the register and the type, in each scope
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
        :return: The next available register as a Value register object
        """
        reg = Value.register(self.reg_counter[-1], len(self.reg_counter) - 1)
        self.reg_counter[-1] += 1
        return reg

    def get_param(self, func, param_num):
        pass

    def get_symbol_operand(self, sym):
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
            r = Operand(func_type, reg)

            instr = Instruction("IMM", a=a, r=r)
            self.write_instr(instr)

            self.reg_table[-1].update({func_name: r})

    def gen_il(self):
        print self.ast
        for stmt in self.ast.children:
            self.gen_stmt(stmt)

        self.write_instr(Instruction("EXIT"))
        return self.program


    def gen_stmt(self, node):
        stmt_kind = node_label(node)

        if re.match("Decl|ShortDecl", stmt_kind):
            self.gen_decl(node)
        if stmt_kind == "Call":
            self.gen_call_stmt(node)

    def gen_funcdef(self, node):
        func_name = node_data(node.children[0])
        func_type = node.children[0].arrowtype
        scope_level = self.current_func.scope_level + 1
        static_scope = self.current_func.static_scope + self.current_func.name





    def gen_call(self, node):
        sym_name = node_data(node.children[0])
        func_op = self.get_symbol_operand(sym_name)

        param_registers = list()
        for expr in node.children[1].children:
            param_instr = self.gen_expr(expr)
            expr_type = expr.arrowtype

            param_op = Operand(expr_type, self.get_register())
            param_instr.set_r(param_op)
            param_registers.append(param_op)

            self.write_instr(param_instr)

        params_op = Operand(
            op_type="({})".format(", ".join(op.operand_type for op in param_registers)),
            op_val=[op.operand_value for op in param_registers]
        )

        return Instruction("CALL", a=func_op, b=params_op)

    def gen_call_stmt(self, node):
        call_instr = self.gen_call(node)
        self.write_instr(call_instr)



    def gen_decl(self, node):
        var_name = node_data(node.children[0])
        var_type = node.children[0].arrowtype

        result_reg = self.get_register()
        r = Operand(var_type, result_reg)

        instr = self.gen_expr(node.children[-1])
        instr.R = r

        self.reg_table[-1][var_name] = r
        self.write_instr(instr)


    def gen_expr(self, node):
        expr_kind = node_label(node)

        # +, -, *, /, or % operators
        if re.match("[+\-*/%]", expr_kind):
            return self.gen_arith_op(node, expr_kind)

        elif re.match("Int|Float|String", expr_kind):
            return self.gen_literal(node)
        elif expr_kind == "Symbol":
            return self.gen_symbol(node)
        elif expr_kind == "Call":
            return self.gen_call(node)
        elif expr_kind == "Cast":
            pass
        elif expr_kind == "Negate":
            return self.gen_negate(node)
        else:
            print node

    def gen_literal(self, node):

        lit_val = node_data(node)
        lit_type = node.arrowtype

        instr = Instruction(
            "IMM",
            a=Operand(str(lit_type), Value.const(lit_type, lit_val)),
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

    def gen_negate(self, node):
        expr_type = node.arrowtype
        reg = self.get_register()

        instr = self.gen_expr(node.children[0])
        instr.set_r(Operand(str(expr_type), reg))
        self.write_instr(instr)

        zero_reg = self.get_register()
        self.write_instr(Instruction(
            "IMM",
            a=Operand(str(expr_type), Value.const(expr_type, 0)),
            r=Operand(expr_type, zero_reg)
        ))

        return Instruction("SUB", a=Operand(expr_type, zero_reg), b=Operand(expr_type, reg))

    def gen_symbol(self, node):
        a = self.get_symbol_operand(node_data(node))
        return Instruction("MV", a=a)









def main():
    il = ILGenerator()
    prog = il.program

    print json.dumps(prog, indent=4, default=json_convert)

if __name__ == '__main__':
    main()







