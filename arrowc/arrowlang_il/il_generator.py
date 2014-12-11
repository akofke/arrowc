#!usr/bin/env python

from il_types import *
import arrowc.arrowlang_types as types
import re
import betterast


def node_label(node):
    """
    Gets the type of the node itself, i.e. "Stmts", "If", "Int", "Symbol", etc
    """
    return re.split(",|:", node.label)[0]


def node_data(node):
    return re.split(",|:", node.label)[1]


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

        # maps a symbol to its parameter position number (1, 2, etc.) for the current funcdef
        self.func_param_table = [dict()]
        self.reg_counter = [0]

        self.program = Program()
        self.func_stack = []

        # self.gen_il()

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

    def current_func(self):
        """
        :rtype: Function
        :return:
        """
        return self.func_stack[-1]

    def init_program(self, main_blk0):

        # possibly change this to only add types when used
        # add all arrowlang primitive types to program types list
        for arr_type in types.prims.itervalues():
            self.program.add_type(arr_type)
        self.program.add_type(types.Type("label"))

        # move all standard library functions into registers, and add their types
        for func_name, func_type in types.library_funcs.iteritems():

            instr = Instruction(
                "IMM",
                a=Operand("label", Value.native_label(func_name)),
                r=Operand(func_type, self.get_register())
            )

            self.write_instr(main_blk0, instr)

            self.reg_table[-1].update({func_name: instr.R})
            self.program.add_type(func_type)

    # change to either a function or method of block
    def write_instr(self, block, instr):
        """

        :type block: BasicBlock
        :type instr: Instruction
        """
        block.instructions.append(instr)
        # self.block_stack[-1].instructions.append(instr)

    def gen_il(self):
        main_func = self.program.add_main()
        self.func_stack.append(main_func)

        # main-b-0
        curr_blk = main_func.add_block()

        # write all boilerplate il code
        self.init_program(curr_blk)

        for stmt in self.ast.children:
            curr_blk = self.gen_stmt(stmt, curr_blk)

        self.write_instr(curr_blk, Instruction("EXIT"))

        # probably change this
        return self.program

    def gen_stmt(self, node, curr_blk):
        stmt_kind = node_label(node)

        if re.match("Decl|ShortDecl", stmt_kind):
            return self.gen_decl(node, curr_blk)

        elif stmt_kind == "AssignStmt":
            return self.gen_asn_stmt(node, curr_blk)

        elif stmt_kind == "Call":
            return self.gen_call_stmt(node, curr_blk)

        elif stmt_kind == "If":
            return self.gen_if(node, curr_blk)

        elif stmt_kind == "For":
            pass

        elif stmt_kind == "FuncDef":
            return self.gen_funcdef(node, curr_blk)

        # these are included in normal stmts since they could not get through the parser
        # if they weren't correctly block stmts
        elif stmt_kind == "Return":
                return self.gen_return(node, curr_blk)

        elif stmt_kind == "Continue":
                pass

        elif stmt_kind == "Break":
                pass

        else:
            print "DEBUG: stmt fell thru  @ " + str(node)
            return None

    def gen_block_stmts(self, node, curr_blk):
        """
        Generates IL for all block statement children of node (which is a "Block" node) and returns
        the final current block

        :param node: a "Block" node
        :param curr_blk:
        :return: the block we end up in
        """
        if node_label(node) != "Block":
            print "DEBUG: expected Block got " + str(node)

        for stmt in node.children:
            curr_blk = self.gen_stmt(stmt, curr_blk)

        return curr_blk

    def gen_for(self, node, curr_blk):
        pass

    def gen_if(self, node, curr_blk):
        then_block = self.current_func().add_block()
        else_block = self.current_func().add_block()

        # if no 'elseIf' stmt, the else block is the exit block
        final_block = else_block

        self.gen_bool_expr(node.children[0].children[0], curr_blk, then_block, else_block)

        last_then_block = self.gen_block_stmts(node.children[1], then_block)

        # if 'elseIf' (child #3) has children
        if len(node.children[2].children) != 0:

            if node_label(node.children[2].children[0]) == "If":
                last_else_blk = self.gen_if(node.children[2].children[0], else_block)
            else:
                last_else_blk = self.gen_block_stmts(node.children[2].children[0], else_block)

            final_block = self.current_func().add_block()
            last_else_blk.add_jump(final_block)

        last_then_block.add_jump(final_block)
        return final_block

    def gen_bool_expr(self, node, curr_blk, then_blk, else_blk):
        expr_kind = node_label(node)

        if node_data(node) == "true":
            curr_blk.add_jump(then_blk)
            return curr_blk

        elif node_data(node) == "false":
            curr_blk.add_jump(else_blk)
            return curr_blk

        elif expr_kind in cmp_ops:
            return self.gen_cmp_op(node, curr_blk, then_blk, else_blk)

        elif expr_kind == "And":
            return self.gen_and(node, curr_blk, then_blk, else_blk)

        elif expr_kind == "Or":
            return self.gen_or(node, curr_blk, then_blk, else_blk)

        elif expr_kind == "Not":
            return self.gen_not(node, curr_blk, then_blk, else_blk)

        else:
            print "DEBUG: bool expr fell through @ " + str(node)

    def gen_cmp_op(self, node, curr_blk, then_blk, else_blk):
        left_expr = self.gen_expr(node.children[0], curr_blk)
        right_expr = self.gen_expr(node.children[1], curr_blk)

        left_expr.set_r(Operand(node.children[0].arrowtype, self.get_register()))
        right_expr.set_r(Operand(node.children[1].arrowtype, self.get_register()))

        self.write_instr(curr_blk, left_expr)
        self.write_instr(curr_blk, right_expr)

        cmp_op = node_label(node)

        curr_blk.add_cmp_jump(cmp_ops[cmp_op], left_expr.R, right_expr.R, then_blk)
        curr_blk.add_jump(else_blk)

        return curr_blk

    def gen_and(self, node, curr_blk, then_blk, else_blk):
        passable_blk = self.gen_bool_expr(node.children[1], self.current_func().add_block(), then_blk, else_blk)
        return self.gen_bool_expr(node.children[0], curr_blk, passable_blk, else_blk)

    def gen_or(self, node, curr_blk, then_blk, else_blk):
        passable_blk = self.gen_bool_expr(node.children[1], self.current_func().add_block(), then_blk, else_blk)
        return self.gen_bool_expr(node.children[0], curr_blk, then_blk, passable_blk)

    def gen_not(self, node, curr_blk, then_blk, else_blk):
        return self.gen_bool_expr(node.children[0], curr_blk, then_blk=else_blk, else_blk=then_blk)

    def gen_asn_stmt(self, node, curr_blk):
        var_oprnd = self.get_symbol_operand(node_data(node.children[0]))
        expr_instr = self.gen_expr(node.children[1], curr_blk)
        expr_instr.set_r(Operand(node.children[1].arrowtype, self.get_register()))
        self.write_instr(curr_blk, expr_instr)

        instr = Instruction("MV", a=expr_instr.R, r=var_oprnd)
        self.write_instr(curr_blk, instr)
        return curr_blk

    def gen_funcdef(self, node, curr_blk):
        func_name = node_data(node.children[0])
        func_type = node.children[0].arrowtype
        scope_level = self.func_stack[-1].scope_level + 1
        static_scope = self.current_func().static_scope[:] + [self.current_func().name]

        func = self.program.add_func(func_name, func_type, scope_level, static_scope)
        func_block = func.add_block()

        instr = Instruction(
            "IMM",
            a=Operand("label", Value.jmp_label(func_block.name, func.name)),
            r=Operand(func_type, self.get_register())
        )

        self.write_instr(curr_blk, instr)
        self.reg_table[-1].update({func_name: instr.R})

        self.func_param_table.append(dict())
        for i, prm_decl in enumerate(node.children[1].children):
            prm_name = node_data(prm_decl.children[0])
            self.func_param_table[-1].update({prm_name: i})

        self.reg_counter.append(0)
        self.reg_table.append(dict())
        self.func_stack.append(func)

        self.gen_block_stmts(node.children[3], func_block)
        # for block_stmt in node.children[3].children:
        #     self.gen_block_stmt(block_stmt, func_block)

        self.func_stack.pop()
        self.reg_table.pop()
        self.reg_counter.pop()

        return curr_blk

    def gen_return(self, node, curr_blk):
        instr = Instruction("RTRN")

        a = Operand()

        if len(node.children) != 0:
            expr_instr = self.gen_expr(node.children[0], curr_blk)
            expr_instr.set_r(Operand(node.children[0].arrowtype, self.get_register()))
            self.write_instr(curr_blk, expr_instr)
            a = expr_instr.R

        instr.set_a(a)
        self.write_instr(curr_blk, instr)
        return curr_blk

    def gen_call(self, node, curr_blk):
        sym_name = node_data(node.children[0])
        func_op = self.get_symbol_operand(sym_name)

        param_registers = list()
        for expr in node.children[1].children:
            param_instr = self.gen_expr(expr, curr_blk)
            expr_type = expr.arrowtype

            param_op = Operand(expr_type, self.get_register())
            param_instr.set_r(param_op)
            param_registers.append(param_op)

            self.write_instr(curr_blk, param_instr)

        params_tuple = types.TupleType([types.prims[op.operand_type] for op in param_registers])
        params_op = Operand(
            op_type=params_tuple,
            op_val=[op.operand_value for op in param_registers]
        )

        self.program.add_type(params_tuple)

        return Instruction("CALL", a=func_op, b=params_op)

    def gen_call_stmt(self, node, curr_blk):
        call_instr = self.gen_call(node, curr_blk)
        self.write_instr(curr_blk, call_instr)
        return curr_blk



    def gen_decl(self, node, curr_blk):
        var_name = node_data(node.children[0])
        var_type = node.children[0].arrowtype

        result_reg = self.get_register()
        r = Operand(var_type, result_reg)

        instr = self.gen_expr(node.children[-1], curr_blk)
        instr.set_r(r)

        self.reg_table[-1][var_name] = r
        self.write_instr(curr_blk, instr)
        return curr_blk


    def gen_expr(self, node, curr_blk):
        """
        :type node: betterast.Node
        :param node:
        :return:
        :rtype Instruction
        """
        expr_kind = node_label(node)
        expr_type = node.arrowtype

        # +, -, *, /, or % operators
        if re.match("[+\-*/%]", expr_kind):
            return self.gen_arith_op(node, expr_kind, curr_blk)

        elif re.match("Int|Float|String", expr_kind):
            return self.gen_literal(node, curr_blk)

        elif expr_kind == "Symbol":
            return self.gen_symbol(node, curr_blk)

        elif expr_kind == "Call":
            return self.gen_call(node, curr_blk)

        elif expr_kind == "Cast":
            return self.gen_cast(node, curr_blk)

        elif expr_kind == "Negate":
            return self.gen_negate(node, curr_blk)

        else:
            print node  # DEBUG

    def gen_literal(self, node, curr_blk):

        lit_val = node_data(node)
        lit_type = node.arrowtype

        instr = Instruction(
            "IMM",
            a=Operand(str(lit_type), Value.const(lit_type, lit_val))
        )

        return instr

    def gen_arith_op(self, node, node_type, curr_blk):
        op = arith_ops[node_type]
        left_instr = self.gen_expr(node.children[0], curr_blk)
        right_instr = self.gen_expr(node.children[1], curr_blk)

        left_instr.set_r(Operand(node.arrowtype, self.get_register()))
        right_instr.set_r(Operand(node.arrowtype, self.get_register()))

        self.write_instr(curr_blk, left_instr)
        self.write_instr(curr_blk, right_instr)

        instr = Instruction(op, a=left_instr.R, b=right_instr.R)
        return instr

    def gen_negate(self, node, curr_blk):
        expr_type = node.arrowtype
        reg = self.get_register()

        instr = self.gen_expr(node.children[0], curr_blk)
        instr.set_r(Operand(str(expr_type), reg))
        self.write_instr(curr_blk, instr)

        zero_reg = self.get_register()
        self.write_instr(curr_blk, Instruction(
            "IMM",
            a=Operand(str(expr_type), Value.const(expr_type, 0)),
            r=Operand(expr_type, zero_reg)
        ))

        return Instruction("SUB", a=Operand(expr_type, zero_reg), b=Operand(expr_type, reg))

    def gen_symbol(self, node, curr_blk):
        sym = node_data(node)
        prm = self.get_param(sym)
        if prm is not None:
            return Instruction("PRM", a=Operand("int32", Value.int_const(prm)))
        else:
            a = self.get_symbol_operand(node_data(node))
            return Instruction("MV", a=a)

    def gen_cast(self, node, curr_blk):
        from_type = node.children[1].arrowtype[0]

        param_instr = self.gen_expr(node.children[1].children[0], curr_blk)
        param_oprnd = Operand(from_type, self.get_register())

        param_instr.set_r(param_oprnd)

        self.write_instr(curr_blk, param_instr)

        return Instruction("CAST", a=param_oprnd)








def main():
    print str(types.prims["int32"])

if __name__ == '__main__':
    main()







