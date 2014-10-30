#!/usr/bin/env python
import string
import betterast


class TypecheckError(Exception):
    pass


class ArrowTypechecker:

    def __init__(self, ast):
        self.scope_stack = [dict()]
        self.ast = ast
        self.int_types = frozenset(("int32", "uint32", "int8", "uint8", "float32"))
        self.cmp_ops = frozenset(("<", "<=", "==", "!=", ">=", ">"))
        self.arith_ops = frozenset(("+", "-", "*", "/", "%"))

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        self.scope_stack.pop()

    def typecheck(self, node):
        node_name = self.parse_node(node)[0]

        if node_name in self.cmp_ops:
            return self.tc_Cmp(node)
        elif node_name in self.arith_ops:
            return self.tc_ArithOp(node)
        else:
            return getattr(self, "tc_" + node_name)(node)

    def typecheck_child(self, node, child_num):
        return self.typecheck(node.children[child_num])

    def append_type(self, type_name, node):
        self.node_append(node, type_name)
        return type_name

    @staticmethod
    def parse_node(node):
        return string.split(node.label, ',')

    def is_undef(self, name):
        if name not in self.scope_stack[-1]:
            return True
        else:
            return False

    @staticmethod
    def node_append(node, label):
        node.label.append(":%s" % label)

    def lookup_symbol(self, sym):
        type_name = None
        for gamma in self.scope_stack:
            if sym in gamma:
                type_name = gamma[sym]

        return type_name

    def tc_Int(self, node):
        return self.append_type("int32", node)

    def tc_Float(self, node):
        node.label.append(":float32")
        return "float32"

    def tc_Boolean(self, node):
        node.label.append(":boolean")
        return "boolean"

    def tc_String(self, node):
        node.label.append(":string")
        return "string"

    def tc_Symbol(self, node):
        sym = self.parse_node(node)[1]

        type_name = self.lookup_symbol(sym)

        if type_name is None:
            raise TypeError

        return self.append_type(type_name, node)

    def tc_Stmts(self, node):
        for child in node.children:
            if self.typecheck(child) != "unit":
                raise TypeError

        return self.append_type("unit", node)

    def tc_FuncDef(self, node):
        pass

    def tc_Decl(self, node):
        name = self.parse_node(node.children[0])[0]

        if self.is_undef(name):
            expr_type = self.typecheck(node.children[2])
            if expr_type != self.tc_Type(node.children[1]):
                raise TypeError

            node.children[0].label.append(":%s" % expr_type)
            self.node_append(node, "unit")
            return "unit"
        else:
            raise TypeError

    def tc_ShortDecl(self, node):
        name = self.parse_node(node.children[0])[0]

        if self.is_undef(name):
            expr_type = self.typecheck(node.children[1])
            node.children[0].label.append(":%s" % expr_type)
            self.node_append(node, "unit")
            return "unit"
        else:
            raise TypeError

    def tc_Type(self, node):
        type = self.parse_node(node.children[0])[1]
        node.children[0].label.append(":%s" % type)
        node.label.append(":%s" % type)
        return type

    def tc_And(self, node):
        if self.typecheck(node.children[0]) == self.typecheck(node.children[1]) == "boolean":
            self.node_append(node, "boolean")
        else:
            raise TypeError

    def tc_Or(self, node):
        if self.typecheck(node.children[0]) == self.typecheck(node.children[1]) == "boolean":
            self.node_append(node, "boolean")
        else:
            raise TypeError

    def tc_Not(self, node):
        if self.typecheck(node.children[0]) == "boolean":
            self.node_append(node, "boolean")
        else:
            raise TypeError

################
    def tc_AssignStmt(self, node):
        name = self.parse_node(node.children[0])[0]

        if self.is_undef(name):
            raise TypeError
        else:
            expr_type = self.typecheck(node.children[1])
            node.children[0].label.append(":%s" % expr_type)
            self.node_append(node, "unit")
            return "unit"



    def tc_DeclExpr(self, node):
        if self.typecheck(node.children[0]) == "unit":
            self.node_append(node, "unit")
        else:
            raise TypeError

    def tc_UpdateExpr(self, node):
        if self.typecheck(node.children[0]) == "unit":
            self.node_append(node, "unit")
        else:
            raise TypeError

    def tc_BooleanExpr(self, node):
        if self.typecheck(node.children[0]) == "boolean":
            self.node_append(node, "boolean")
        else:
            raise TypeError


    def tc_Return(self, node):
        pass

    def tc_If(self, node):
        condition_type = self.typecheck_child(node, 0)
        then_type = self.typecheck_child(node, 1)
        else_type = self.typecheck_child(node, 2)

        if condition_type == "boolean" and then_type == else_type == "unit":
            return self.append_type("unit", node)
        else:
            raise TypeError

    def tc_ElseIf(self, node):
            if self.typecheck_child(node, 0) == "unit":
                return self.append_type("unit", node)
            else:
                raise TypeError

    def tc_For(self, node):
        self.push_scope()

        decl_type = self.typecheck_child(node, 0)
        bool_type = self.typecheck_child(node, 1)
        update_type = self.typecheck_child(node, 2)
        block_type = self.typecheck_child(node, 3)

        if decl_type == update_type == block_type == "unit" and bool_type == "boolean":
            return self.append_type("unit", node)
        else:
            raise TypecheckError

    def tc_Block(self, node):
        pass

    def tc_Cmp(self, node):
        if self.typecheck(node.children[0]) == self.typecheck(node.children[1]):
            self.node_append(node, "boolean")

    def tc_Call(self, node):
        pass

    def tc_Cast(self, node):
        pass

    def tc_ArithOp(self, node):
        type1, type2 = self.typecheck(node.children[0]), self.typecheck(node.children[1])
        if type1 == type2 and type1 in self.int_types:
            self.node_append(":%s" % type1)
            return type1
        else:
            raise TypeError

    def tc_Negate(self, node):
        type_name = self.typecheck(node.children[0])
        if type_name in self.int_types:
            return self.append_type(type_name, node)


    def tc_Error(self, node):
        pass
















