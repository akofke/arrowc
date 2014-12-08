#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types
import re
import json
import betterast


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

cmp_ops = {
    "==": "IFEQ",
    "!=": "IFNE",
    "<": "IFLT",
    ">": "IFGT",
    "<=": "IFLE",
    ">=": "IFGE"
}


class ILGenerator():
    def __init__(self, typed_ast):
        """
        :type typed_ast: betterast.Node
        :param typed_ast: the typechecked abstract syntax tree
        """
        self.ast = typed_ast

        # maps symbols to Operands, i.e. the register and the type, in each scope
        self.reg_table = [dict()]
        self.func_param_table = [dict()]
        self.reg_counter = [0]

        self.program = Program()
        self.func_stack = []
        self.block_stack = []
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

    def get_param(self, sym_name):
        if sym_name in self.func_param_table[-1]:
            return self.func_param_table[-1][sym_name]
        else:
            return None

    def get_symbol_operand(self, sym):
        for d in self.reg_table:
            if sym in d:
                return d[sym]


    def get_current_func(self):
        """
        :rtype Function
        :return:
        """
        return self.func_stack[-1]

    # def write_instr(self, op, **operands):
    #     self.current_block.add_instr(op, **operands)

    def write_instr(self, instr):
        self.block_stack[-1].instructions.append(instr)

    def init_program(self):

        # add all arrowlang primitive types to program types list
        self.program.types.update((name, ArrowType(val)) for name, val in types.prims.iteritems())

        self.program.add_type(types.Type("label"))

        main_func = self.program.add_main()
        main_b0 = main_func.add_block()
        self.func_stack.append(main_func)
        self.block_stack.append(main_b0)

        for func_name, func_type in types.library_funcs.iteritems():
            a = Operand("label", Value.native_label(func_name))

            reg = self.get_register()
            r = Operand(func_type, reg)

            instr = Instruction("IMM", a=a, r=r)
            self.write_instr(instr)

            self.reg_table[-1].update({func_name: r})
            self.program.add_type(func_type)

    def gen_il(self):
        # print self.ast
        for stmt in self.ast.children:
            self.gen_stmt(stmt)

        self.write_instr(Instruction("EXIT"))
        return self.program


    def gen_stmt(self, node):
        stmt_kind = node_label(node)

        if re.match("Decl|ShortDecl", stmt_kind):
            self.gen_decl(node)
        elif stmt_kind == "AssignStmt":
            self.gen_asn_stmt(node)
        elif stmt_kind == "Call":
            self.gen_call_stmt(node)
        elif stmt_kind == "If":
            pass
        elif stmt_kind == "For":
            pass
        elif stmt_kind == "FuncDef":
            self.gen_funcdef(node)
        else:
            return None

    def gen_if(self, node):
        then_block = self.func_stack[-1].add_block()
        else_block = self.func_stack[-1].add_block()
        final_block = self.func_stack[-1].add_block()

    def gen_bool_expr(self, node, then_blk, else_blk):
        pass



    def gen_asn_stmt(self, node):
        var_oprnd = self.get_symbol_operand(node_data(node.children[0]))
        expr_oprnd = self.gen_expr(node.children[1])

        instr = Instruction("IMM", a=expr_oprnd, r=var_oprnd)
        self.write_instr(instr)

    def gen_block_stmt(self, node):
        if not self.gen_stmt(node):
            if node_label(node) == "Return":
                self.gen_return(node)
            if node_label(node) == "Continue":
                pass
            if node_label(node) == "Break":
                pass

    def gen_funcdef(self, node):
        func_name = node_data(node.children[0])
        func_type = node.children[0].arrowtype
        scope_level = self.func_stack[-1].scope_level + 1
        # static_scope = list(self.current_func.static_scope).append(self.current_func.name)
        static_scope = ["main"]

        func = self.program.add_func(func_name, func_type, scope_level, static_scope=static_scope)
        func_block = func.add_block()

        instr = Instruction(
            "IMM",
            a=Operand("label", Value.jmp_label(func_block.name, func.name)),
            r=Operand(func_type, self.get_register())
        )

        self.write_instr(instr)
        self.reg_table[-1].update({func_name: instr.R})

        self.func_param_table.append(dict())
        for i, prm_decl in enumerate(node.children[1].children):
            prm_name = node_data(prm_decl.children[0])
            self.func_param_table[-1].update({prm_name: i})

        self.reg_counter.append(0)
        self.reg_table.append(dict())
        self.func_stack.append(func)
        self.block_stack.append(func_block)

        for block_stmt in node.children[3].children:
            self.gen_block_stmt(block_stmt)

        self.block_stack.pop()
        self.func_stack.pop()
        self.reg_table.pop()
        self.reg_counter.pop()

    def gen_return(self, node):
        instr = Instruction("RTRN")

        a = Operand()

        if len(node.children) != 0:
            expr_instr = self.gen_expr(node.children[0])
            expr_instr.set_r(Operand(node.children[0].arrowtype, self.get_register()))
            self.write_instr(expr_instr)
            a = expr_instr.R

        instr.set_a(a)
        self.write_instr(instr)






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

        params_tuple = types.TupleType([types.prims[op.operand_type] for op in param_registers])
        params_op = Operand(
            op_type=params_tuple,
            op_val=[op.operand_value for op in param_registers]
        )

        self.program.add_type(params_tuple)

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
        instr.set_r(r)

        self.reg_table[-1][var_name] = r
        self.write_instr(instr)


    def gen_expr(self, node):
        """
        :type node: betterast.Node
        :param node:
        :return:
        :rtype Instruction
        """
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
            return self.gen_cast(node)

        elif expr_kind == "Negate":
            return self.gen_negate(node)

        else:
            print node  # DEBUG

    def gen_literal(self, node):

        lit_val = node_data(node)
        lit_type = node.arrowtype

        instr = Instruction(
            "IMM",
            a=Operand(str(lit_type), Value.const(lit_type, lit_val))
        )

        return instr

    def gen_arith_op(self, node, node_type):
        op = arith_ops[node_type]
        left_instr = self.gen_expr(node.children[0])
        right_instr = self.gen_expr(node.children[1])

        left_instr.set_r(Operand(node.arrowtype, self.get_register()))
        right_instr.set_r(Operand(node.arrowtype, self.get_register()))

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
        sym = node_data(node)
        prm = self.get_param(sym)
        if prm is not None:
            return Instruction("PRM", a=Operand("int32", Value.int_const(prm)))
        else:
            a = self.get_symbol_operand(node_data(node))
            return Instruction("MV", a=a)

    def gen_cast(self, node):
        from_type = node.children[1].arrowtype[0]

        print from_type

        param_instr = self.gen_expr(node.children[1].children[0])
        param_oprnd = Operand(from_type, self.get_register())

        param_instr.set_r(param_oprnd)

        self.write_instr(param_instr)

        return Instruction("CAST", a=param_oprnd)








def main():
    print str(types.prims["int32"])

if __name__ == '__main__':
    main()







