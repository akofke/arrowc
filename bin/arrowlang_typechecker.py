#!/usr/bin/env python
import string
import betterast


class Typechecker:
    def __init__(self, ast):
        self.scope_stack = [dict()]
        self.ast = ast

    def typecheck(self, node):
        return getattr(self, "tc_" + self.parse_node(node)[0])(node)

    @staticmethod
    def parse_node(node):
        return string.split(node.label, ',')

    def undef(self, name):
        if name not in self.scope_stack[-1]:
            return True
        else:
            return False

    @staticmethod
    def node_append(node, label):
        node.label.append(":%s" % label)

    def tc_Int(self, node):
        node.label.append(":int32")
        return "int32"

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

        type = None
        for gamma in self.scope_stack:
            if sym in gamma:
                type = gamma[sym]

        if type is None:
            raise TypeError

        node.label.append(":%s" % type)
        return type

    def tc_Stmts(self, node):
        for child in node.children:
            if self.typecheck(child) != "unit":
                raise TypeError

        node.label.append(":unit")
        return "unit"

    def tc_FuncDef(self, node):
        pass

    def tc_Decl(self, node):
        name = self.parse_node(node.children[0])[0]

        if self.undef(name):
            expr_type = self.typecheck(node.children[2])
            if expr_type != self.tc_Type(node.children[1]):
                raise TypeError

            node.children[0].label.append(":%s" % expr_type)
            self.node_append(node, "unit")

    def tc_ShortDecl(self, node):
        name = self.parse_node(node.children[0])[0]

        if self.undef(name):
            expr_type = self.typecheck(node.children[1])
            node.children[0].label.append(":%s" % expr_type)
            self.node_append(node, "unit")


    def tc_Type(self, node):
        type = self.parse_node(node.children[0])[1]
        node.children[0].label.append(":%s" % type)
        node.label.append(":%s" % type)
        return type












