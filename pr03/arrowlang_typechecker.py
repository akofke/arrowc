#!/usr/bin/env python
import string
import betterast


def parse_node(node):
    return string.split(node.label, ',')


def append_type(type_obj, node):
    node_append(node, str(type_obj))
    return type_obj


def node_append(node, label):
    node.label += ":%s" % label


class ArrowTypechecker:
    def __init__(self, ast):
        self.scope_stack = [dict()]
        self.enclosing_funcdef = list()
        self.ast = ast

        self.prims = {
            "unit": SizedType("unit", 0),
            "boolean": SizedType("boolean", 1),
            "int32": IntType("int32", 32, True),
            "uint32": IntType("uint32", 32, False),
            "int8": IntType("int8", 8, True),
            "uint8": IntType("uint32", 8, False),
            "float32": SizedType("float32", 32),
            "string": Type("string")
        }

        self.scope_stack[0].update({
            "print_int32": FuncType((self.prims["int32"],), self.prims["unit"]),
            "print_uint32": FuncType((self.prims["uint32"],), self.prims["unit"]),
            "print_int8": FuncType((self.prims["int8"],), self.prims["unit"]),
            "print_uint8": FuncType((self.prims["uint8"],), self.prims["unit"]),
            "print_float32": FuncType((self.prims["float32"],), self.prims["unit"]),
            "print": FuncType((self.prims["string"],), self.prims["unit"])
        })

        self.num_types = frozenset((
            self.prims["int32"],
            self.prims["uint32"],
            self.prims["int8"],
            self.prims["uint8"],
            self.prims["float32"]
        ))

        self.cmp_ops = frozenset(("<", "<=", "==", "!=", ">=", ">"))
        self.arith_ops = frozenset(("+", "-", "*", "/", "%"))

    def typecheck(self):
        self.tc_Stmts(self.ast)
        return self.ast

    def push_scope(self):
        self.scope_stack.append(dict())

    def pop_scope(self):
        self.scope_stack.pop()

    def add_symbol(self, sym_name, sym_type):
        self.scope_stack[-1].update({sym_name: sym_type})

    def typecheck_node(self, node):
        node_name = parse_node(node)[0]

        if node_name in self.cmp_ops:
            return self.tc_Cmp(node)
        elif node_name in self.arith_ops:
            return self.tc_ArithOp(node)
        else:
            return getattr(self, "tc_" + node_name)(node)

    def typecheck_child(self, node, child_num):
        return self.typecheck_node(node.children[child_num])

    def is_undef(self, name):
        if name not in self.scope_stack[-1]:
            return True
        else:
            return False

    def is_undef_all(self, name):
        for gamma in self.scope_stack:
            if name in gamma:
                return False

        return True

    def lookup_symbol(self, sym):
        type_obj = None
        for gamma in self.scope_stack:
            if sym in gamma:
                type_obj = gamma[sym]

        return type_obj

    def tc_Int(self, node):
        return append_type(self.prims["int32"], node)

    def tc_Float(self, node):
        return append_type(self.prims["float32"], node)

    def tc_Boolean(self, node):
        return append_type(self.prims["boolean"], node)

    def tc_String(self, node):
        return append_type(self.prims["string"], node)

    def tc_Symbol(self, node):
        sym = parse_node(node)[1]

        sym_type = self.lookup_symbol(sym)

        if sym_type is None:
            raise TypecheckError

        return append_type(sym_type, node)

    def tc_Stmts(self, node):
        for child in node.children:
            if self.typecheck_node(child) != self.prims["unit"]:
                raise TypecheckError

        return append_type(self.prims["unit"], node)

    def tc_ParamDecls(self, node):
        type_list = list()
        for child in node.children:
            type_list.append(self.tc_ParamDecl(child))

        return append_type(tuple(type_list), node)

    def tc_ParamDecl(self, node):
        name = parse_node(node.children[0])[0]
        if self.is_undef(name):
            asserted_type = self.tc_Type(node.children[1])
            self.add_symbol(name, asserted_type)
            return append_type(asserted_type, node.children[0])
        else:
            raise TypecheckError

    def tc_ReturnType(self, node):
        return append_type(self.typecheck_child(node, 0), node)

    def tc_FuncDef(self, node):
        name = parse_node(node.children[0])[0]
        if self.is_undef(name):
            self.push_scope()

            param_types = self.tc_ParamDecls(node.children[1])
            return_type = self.tc_ReturnType(node.children[2])
            func_type = FuncType(param_types, return_type)

            self.add_symbol(name, func_type)
            self.enclosing_funcdef.append(func_type)
            block_type = self.tc_Block(node.children[3])

            if block_type != self.prims["unit"]:
                raise TypecheckError

            self.pop_scope()
            self.enclosing_funcdef.pop()
            self.add_symbol(name, func_type)
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError

    def tc_Decl(self, node):
        name = parse_node(node.children[0])[0]

        if self.is_undef(name):
            aserted_type = self.tc_Type(node.children[1])
            expr_type = self.typecheck_child(node, 2)

            if expr_type != aserted_type:
                raise TypecheckError

            append_type(aserted_type, node.children[0])
            self.add_symbol(name, aserted_type)
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError

    def tc_ShortDecl(self, node):
        name = parse_node(node.children[0])[0]

        if self.is_undef(name):
            expr_type = self.typecheck_child(node, 1)
            append_type(expr_type, node.children[0])
            self.add_symbol(name, expr_type)
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError

    def tc_Type(self, node):
        type_name = parse_node(node.children[0])[1]
        if type_name in self.prims.keys():
            type_obj = self.prims[type_name]
            node_append(node.children[0], type_name)
            return append_type(type_obj, node)
        else:
            raise TypecheckError

    def tc_And(self, node):
        if self.typecheck_child(node, 0) == self.typecheck_child(node, 1) == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError

    def tc_Or(self, node):
        if self.typecheck_child(node, 0) == self.typecheck_child(node, 1) == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError

    def tc_Not(self, node):
        if self.typecheck_child(node, 0) == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError

    def tc_AssignStmt(self, node):
        name = parse_node(node.children[0])[0]
        name_type = self.lookup_symbol(name)

        if name_type is not None:
            expr_type = self.typecheck_child(node, 1)
            if name_type == expr_type:
                append_type(name_type, node.children[0])
                return append_type(self.prims["unit"], node)
            else:
                raise TypecheckError
        else:
            raise TypecheckError

    def tc_Return(self, node):
        expected_return = self.enclosing_funcdef[-1].return_type

        if len(node.children) != 0:
            returns_type = self.typecheck_child(node, 0)
        else:
            returns_type = self.prims["unit"]

        if returns_type == expected_return:
            return append_type(returns_type, node)
        else:
            raise TypecheckError

    def tc_If(self, node):
        condition_type = self.typecheck_child(node, 0)
        then_type = self.typecheck_child(node, 1)
        else_type = self.typecheck_child(node, 2)

        if condition_type == self.prims["boolean"] and then_type == else_type == self.prims["unit"]:
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError

    def tc_ElseIf(self, node):
        if len(node.children) != 0:
            if self.typecheck_child(node, 0) == self.prims["unit"]:
                return append_type("unit", node)
            else:
                raise TypecheckError
        else:
            return append_type(self.prims["unit"], node)

    def tc_DeclExpr(self, node):
        if len(node.children) != 0:
            if self.typecheck_node(node.children[0]) == self.prims["unit"]:
                return append_type(self.prims["unit"], node)
            else:
                raise TypecheckError
        else:
            return append_type(self.prims["unit"], node)

    def tc_UpdateExpr(self, node):
        if len(node.children) != 0:
            if self.typecheck_node(node.children[0]) == self.prims["unit"]:
                return append_type(self.prims["unit"], node)
            else:
                raise TypecheckError
        else:
            return append_type(self.prims["unit"], node)

    def tc_BooleanExpr(self, node):
        if self.typecheck_child(node, 0) == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError

    def tc_For(self, node):
        self.push_scope()

        decl_type = self.typecheck_child(node, 0)
        bool_type = self.typecheck_child(node, 1)
        update_type = self.typecheck_child(node, 2)
        block_type = self.typecheck_child(node, 3)

        if decl_type == update_type == block_type == self.prims["unit"] \
                and bool_type == self.prims["boolean"]:

            self.pop_scope()
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError

    def tc_Block(self, node):
        self.push_scope()

        for child in node.children:
            if self.typecheck_node(child) != self.prims["unit"]:
                raise TypecheckError

        self.pop_scope()
        return append_type(self.prims["unit"], node)

    def tc_Params(self, node):
        type_list = list()
        for child in node.children:
            type_list.append(self.typecheck_node(child))

        return append_type(tuple(type_list), node)

    def tc_Call(self, node):
        func_name = parse_node(node.children[0])[0]
        func_type = self.lookup_symbol(func_name)

        for t in self.num_types:
            if func_name == t.name:
                return self.tc_Cast(node, t)

        if func_type is not None:
            param_types = self.tc_Params(node.children[1])
            if param_types == func_type.params:
                append_type(func_type, node.children[0])
                return append_type(func_type.return_type, node)
            else:
                raise TypecheckError
        else:
            raise TypecheckError

    def tc_Cast(self, node, num_type):
        if len(node.children[1].children) == 1:
            param_type = self.tc_Params(node.children[1])  # singleton tuple
            if param_type[0] in self.num_types:
                cast_type = FuncType(param_type, num_type)
                append_type(cast_type, node.children[0])
                node.label = "Cast"
                return append_type(cast_type, node)
            else:
                raise TypecheckError
        else:
            raise TypecheckError

    def tc_Cmp(self, node):
        type1, type2 = self.typecheck_child(node, 0), self.typecheck_child(node, 1)
        if type1 == type2 and type1 in self.num_types:
            return append_type(type1, node)

    def tc_ArithOp(self, node):
        type1, type2 = self.typecheck_child(node, 0), self.typecheck_child(node, 1)
        if type1 == type2 and type1 in self.num_types:
            return append_type(type1, node)
        else:
            raise TypecheckError

    def tc_Negate(self, node):
        type_obj = self.typecheck_node(node.children[0])
        if type_obj in self.num_types:
            return append_type(type_obj, node)

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

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


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
    def __init__(self, params, return_type):

        self.params = params
        self.return_type = return_type
        Type.__init__(self, str(self))

    def __eq__(self, other):
        if type(other) is type(self):
            return self.name == other.name and self.params == other.params and self.return_type == other.return_type
        else:
            return False

    def __str__(self):
        return "fn({!s})->{}".format(tuple(self.params), self.return_type)
