#!/usr/bin/env python
import string
import betterast


def parse_node(node):
    return string.split(node.label, ',')


def append_type(type_obj, node):
    node_append(node, type_obj.name)
    return type_obj


def node_append(node, label):
    node.label.append(":%s" % label)

class ArrowTypechecker:

    def __init__(self, ast):
        self.scope_stack = [dict()]
        self.ast = ast
        #self.int_types = frozenset(("int32", "uint32", "int8", "uint8", "float32"))

        self.prim_types = {
            "unit": SizedType("unit", 0),
            "boolean": SizedType("boolean", 1),
            "int32": IntType("int32", 32, True),
            "uint32": IntType("uint32", 32, False),
            "int8": IntType("int8", 8, True),
            "uint8": IntType("uint32", 8, False),
            "float32": SizedType("float32", 32),
            "string": Type("string")
        }

        self.num_types = frozenset((
            self.prim_types["int32"],
            self.prim_types["uint32"],
            self.prim_types["int8"],
            self.prim_types["uint8"],
            self.prim_types["float32"]
        ))

        self.cmp_ops = frozenset(("<", "<=", "==", "!=", ">=", ">"))
        self.arith_ops = frozenset(("+", "-", "*", "/", "%"))

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        self.scope_stack.pop()

    def add_symbol(self, sym_name, sym_type):
        self.scope_stack[-1].update({sym_name: sym_type})

    def typecheck(self, node):
        node_name = parse_node(node)[0]

        if node_name in self.cmp_ops:
            return self.tc_Cmp(node)
        elif node_name in self.arith_ops:
            return self.tc_ArithOp(node)
        else:
            return getattr(self, "tc_" + node_name)(node)

    def typecheck_child(self, node, child_num):
        return self.typecheck(node.children[child_num])

    def is_undef(self, name):
        if name not in self.scope_stack[-1]:
            return True
        else:
            return False

    def lookup_symbol(self, sym):
        type_obj = None
        for gamma in self.scope_stack:
            if sym in gamma:
                type_obj = gamma[sym]

        return type_obj

    def tc_Int(self, node):
        return append_type(self.prim_types["int32"], node)

    def tc_Float(self, node):
        return append_type(self.prim_types["float32"], node)

    def tc_Boolean(self, node):
        return append_type(self.prim_types["boolean"], node)

    def tc_String(self, node):
        return append_type(self.prim_types["string"], node)

    def tc_Symbol(self, node):
        sym = parse_node(node)[1]

        sym_type = self.lookup_symbol(sym)

        if sym_type is None:
            raise TypeError

        return append_type(sym_type, node)

    def tc_Stmts(self, node):
        for child in node.children:
            if self.typecheck(child) != self.prim_types["unit"]:
                raise TypeError

        return append_type(self.prim_types["unit"], node)

    def tc_FuncDef(self, node):
        pass

    def tc_Decl(self, node):
        name = parse_node(node.children[0])[0]

        if self.is_undef(name):
            aserted_type = self.tc_Type(node.children[1])
            expr_type = self.typecheck_child(node, 2)

            if expr_type != aserted_type:
                raise TypeError

            append_type(aserted_type, node.children[0])

            return append_type(self.prim_types["unit"])
        else:
            raise TypeError

    def tc_ShortDecl(self, node):
        name = parse_node(node.children[0])[0]

        if self.is_undef(name):
            expr_type = self.typecheck(node.children[1])
            node.children[0].label.append(":%s" % expr_type)
            node_append(node, "unit")
            return "unit"
        else:
            raise TypeError

    def tc_Type(self, node):
        type_name = parse_node(node.children[0])[1]
        if type_name in self.prim_types.keys():
            type_obj = self.prim_types[type_name]
            node_append(node.children[0], type_name)
            return append_type(type_obj, node)
        else:
            raise TypecheckError

    def tc_And(self, node):
        if self.typecheck_child(node, 0) == self.typecheck_child(node, 1) == self.prim_types["boolean"]:
            return append_type(self.prim_types["boolean"], node)
        else:
            raise TypeError

    def tc_Or(self, node):
        if self.typecheck_child(node, 0) == self.typecheck_child(node, 1) == self.prim_types["boolean"]:
            return append_type(self.prim_types["boolean"], node)
        else:
            raise TypeError

    def tc_Not(self, node):
        if self.typecheck_child(node, 0) == self.prim_types["boolean"]:
            return append_type(self.prim_types["boolean"], node)
        else:
            raise TypeError

################
    def tc_AssignStmt(self, node):
        name = parse_node(node.children[0])[0]

        if self.is_undef(name):
            raise TypeError
        else:
            expr_type = self.typecheck(node.children[1])
            node.children[0].label.append(":%s" % expr_type)
            node_append(node, "unit")
            return "unit"



    def tc_DeclExpr(self, node):
        if self.typecheck(node.children[0]) == "unit":
            node_append(node, "unit")
        else:
            raise TypeError

    def tc_UpdateExpr(self, node):
        if self.typecheck(node.children[0]) == "unit":
            node_append(node, "unit")
        else:
            raise TypeError

    def tc_BooleanExpr(self, node):
        if self.typecheck(node.children[0]) == "boolean":
            node_append(node, "boolean")
        else:
            raise TypeError


    def tc_Return(self, node):
        pass

    def tc_If(self, node):
        condition_type = self.typecheck_child(node, 0)
        then_type = self.typecheck_child(node, 1)
        else_type = self.typecheck_child(node, 2)

        if condition_type == "boolean" and then_type == else_type == "unit":
            return append_type("unit", node)
        else:
            raise TypeError

    def tc_ElseIf(self, node):
            if self.typecheck_child(node, 0) == "unit":
                return append_type("unit", node)
            else:
                raise TypeError

    def tc_For(self, node):
        self.push_scope()

        decl_type = self.typecheck_child(node, 0)
        bool_type = self.typecheck_child(node, 1)
        update_type = self.typecheck_child(node, 2)
        block_type = self.typecheck_child(node, 3)

        if decl_type == update_type == block_type == "unit" and bool_type == "boolean":
            self.pop_scope()
            return append_type("unit", node)
        else:
            raise TypecheckError

    def tc_Block(self, node):
        self.push_scope()

        for child in node.children:
            if self.typecheck(child) != "unit":
                raise TypecheckError

        self.pop_scope()
        return append_type("unit", node)

    def tc_Cmp(self, node):
        if self.typecheck(node.children[0]) == self.typecheck(node.children[1]):
            node_append(node, "boolean")

    def tc_Call(self, node):
        pass

    def tc_Cast(self, node):
        pass

    def tc_ArithOp(self, node):
        type1, type2 = self.typecheck(node.children[0]), self.typecheck(node.children[1])
        if type1 == type2 and type1 in self.int_types:
            node_append(":%s" % type1)
            return type1
        else:
            raise TypeError

    def tc_Negate(self, node):
        type_name = self.typecheck(node.children[0])
        if type_name in self.int_types:
            return append_type(type_name, node)


    def tc_Error(self, node):
        pass


class TypecheckError(Exception):
    pass


class Type:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if type(other) is type(self):
            return other.name == self.name
        else:
            return False


class SizedType(Type):
    def __init__(self, name, size):
        Type.__init__(self, name)
        self.size = size

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.size == other.size
        else:
            return False


class IntType(Type):
    def __init__(self, name, size, signed):
        Type.__init__(self, name)
        self.size = size
        self.signed = signed

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.size == other.size and self.signed == other.signed
        else:
            return False


class FuncType(Type):
    def __init__(self, name, params, return_type):
        Type.__init__(self, name)
        self.params = params
        self.return_type = return_type

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.params == other.params and self.return_type == other.return_type
        else:
            return False

















