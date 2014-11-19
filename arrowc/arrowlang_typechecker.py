#!/usr/bin/env python
import string
from arrowlang_types import *


def parse_node(node):
    """
    returns a list of the words in the node, split around ','.
    e.g. the node "Int,3" returns ["Int", 3]
    """
    return string.split(node.label, ',')


def append_type(type_obj, node):
    """
    Appends the string representation of the given type to the given node. Returns
    the type object so at the end of each typechecking function, the type can be appended
    and returned in one statement.

    :param type_obj: A Type object or string to be appended.
    :param node: The Node object to be labelled with the type
    :return: The given Type object
    """
    node.label += ":{!s}".format(type_obj)
    return type_obj


def append_typeList(type_list, node):
    """
    Same as append_type, but with a list of types for params, etc.
    """
    list_str = ', '.join(map(str, type_list))
    node.label += ":({})".format(list_str)
    return type_list


class ArrowTypechecker:
    def __init__(self, ast):
        """
        Creates a typechecker for the given Arrowlang abstract syntax tree. The typechecker initially
        contains the Arrowlang primitive types as types, and the Arrowlang standard library as functions
        in the global scope.

        The syntax tree is assumed to be one that has been produced from the Arrowlang parser. An arbitary
        tree that has syntax errors could cause undefined behavior.

        :param ast: The betterast syntax tree that is produced by the parser.
        :return: creates a new typechecker object with the given ast, ready for type checking.
        """
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
        """
        Runs typechecking methods over the whole tree, appending type information to each node and returns
        the updated tree.
        :return: The now-typed syntax tree.
        """
        self.tc_Stmts(self.ast)
        return self.ast

    def typecheck_node(self, node):
        """
        Runs the correct typechecking method for the given node. If the node name is a comparison or
        arithmetic operator it goes to their respective methods, and if not it uses reflection to find the
        method corresponding to the node name.

        :param node: The node to be typechecked.
        :return: The result of the typechecking method.
        """

        node_name = parse_node(node)[0]

        if node_name in self.cmp_ops:
            return self.tc_Cmp(node)
        elif node_name in self.arith_ops:
            return self.tc_ArithOp(node)
        else:
            return getattr(self, "tc_" + node_name)(node)

    def typecheck_child(self, node, child_num):
        """
        Runs the typecheck_node method on the node's child with the given index in the child list.
        """
        return self.typecheck_node(node.children[child_num])

    def push_scope(self):
        """
        Appends a new scope dictionary to the top of the stack.
        """
        self.scope_stack.append(dict())

    def pop_scope(self):
        """
        Removes a scope from the top of the stack
        """
        self.scope_stack.pop()

    def add_symbol(self, sym_name, sym_type):
        """
        Adds the symbol name and type to the current active scope.
        :param sym_name: The string name of the symbol
        :param sym_type: The Type of the symbol.
        """
        self.scope_stack[-1].update({sym_name: sym_type})

    def is_undef(self, name):
        """
        Returns whether the given name is defined in the current scope. Does not check any higher scopes.
        """
        if name not in self.scope_stack[-1]:
            return True
        else:
            return False

    def is_undef_all(self, name):
        """
        Returns whether the given name is defined in any scope.
        """
        for gamma in self.scope_stack:
            if name in gamma:
                return False

        return True

    def lookup_symbol(self, sym):
        """
        Looks up the given symbol in the scope stack and returns the
        Type object mapped to it. If it is not defined returns None.
        """
        type_obj = None
        for gamma in self.scope_stack:
            if sym in gamma:
                type_obj = gamma[sym]

        return type_obj

    # Primitive literals and symbol
    ######################################################################

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
            raise TypecheckError("At '{}', cannot find symbol '{}'".format(node.label, sym))

        return append_type(sym_type, node)

    # Stmts, Type, Block
    ######################################################################

    def tc_Stmts(self, node):
        for child in node.children:
            child_type = self.typecheck_node(child)
            if child_type != self.prims["unit"]:
                raise TypecheckError("At '{}', expected 'unit' but got '{!s}'".format(node.label, child_type))

        return append_type(self.prims["unit"], node)

    def tc_Type(self, node):
        type_name = parse_node(node.children[0])[1]
        if type_name in self.prims.keys():
            type_obj = self.prims[type_name]
            # node_append(node.children[0], type_name)
            append_type(type_name, node.children[0])
            return append_type(type_obj, node)
        else:
            raise TypecheckError("Unknown type '{}'".format(type_name))

    def tc_Block(self, node):
        self.push_scope()

        for child in node.children:
            child_type = self.typecheck_node(child)
            if child_type != self.prims["unit"]:
                raise TypecheckError("At 'Block', expected 'unit' but got {!s}".format(child_type))

        self.pop_scope()
        return append_type(self.prims["unit"], node)

    # Funcdef and helper typechecks
    ######################################################################

    def tc_ParamDecls(self, node):
        type_list = list()
        for child in node.children:
            type_list.append(self.tc_ParamDecl(child))

        return append_typeList(tuple(type_list), node)

    def tc_ParamDecl(self, node):
        name = parse_node(node.children[0])[1]
        if self.is_undef(name):
            declared_type = self.tc_Type(node.children[1])
            self.add_symbol(name, declared_type)
            append_type(declared_type, node.children[0])
            return append_type(declared_type, node)
        else:
            raise TypecheckError("At '{}', parameter '{}' is already defined in scope".format(node.label, name))

    def tc_ReturnType(self, node):
        return append_type(self.typecheck_child(node, 0), node)

    def tc_FuncDef(self, node):
        name = parse_node(node.children[0])[1]
        if self.is_undef(name):
            self.push_scope()

            param_types = self.tc_ParamDecls(node.children[1])
            return_type = self.tc_ReturnType(node.children[2])
            func_type = FuncType(param_types, return_type)

            self.add_symbol(name, func_type)
            self.enclosing_funcdef.append(func_type)
            block_type = self.tc_Block(node.children[3])

            if block_type != self.prims["unit"]:
                raise TypecheckError("For function block expected 'unit' but got {!s}".format(block_type))

            self.pop_scope()
            self.enclosing_funcdef.pop()

            self.add_symbol(name, func_type)
            append_type(func_type, node.children[0])
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError("At '{}', name '{}' is redefined in same scope".format(node.label, name))

    # Decl, ShortDecl, Assign, and Return statements
    ######################################################################

    def tc_Decl(self, node):
        name = parse_node(node.children[0])[1]

        if self.is_undef(name):
            declared_type = self.tc_Type(node.children[1])
            expr_type = self.typecheck_child(node, 2)

            if expr_type != declared_type:
                raise TypecheckError(
                    "At '{}', declared type '{!s}' does not agree with expression type '{!s}'"
                    .format(node.label, declared_type, expr_type)
                )

            append_type(declared_type, node.children[0])
            self.add_symbol(name, declared_type)
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError("At '{}, name '{}' is redefined in same scope".format(node.label, name))

    def tc_ShortDecl(self, node):
        name = parse_node(node.children[0])[1]

        if self.is_undef(name):
            expr_type = self.typecheck_child(node, 1)
            append_type(expr_type, node.children[0])
            self.add_symbol(name, expr_type)
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError("At '{}, name '{}' is redefined in same scope".format(node.label, name))

    def tc_AssignStmt(self, node):
        name = parse_node(node.children[0])[1]
        name_type = self.lookup_symbol(name)

        if name_type is not None:
            expr_type = self.typecheck_child(node, 1)
            if name_type == expr_type:
                append_type(name_type, node.children[0])
                return append_type(self.prims["unit"], node)
            else:
                raise TypecheckError(
                    "At '{}', variable '{}' type '{!s}' does not agree with expression type '{}'"
                    .format(node.label, name, name_type, expr_type)
                )
        else:
            raise TypecheckError("At '{}', name '{}' is not defined".format(node.label, name))

    def tc_Return(self, node):
        expected_return = self.enclosing_funcdef[-1].return_type

        if len(node.children) != 0:
            returns_type = self.typecheck_child(node, 0)
        else:
            returns_type = self.prims["unit"]

        if returns_type == expected_return:
            return append_type(self.prims["unit"], node)
        else:
            raise TypecheckError(
                "Return type '{!s}' does not agree with expected return type '{!s}'"
                .format(returns_type, expected_return)
            )

    # If, For statements and helper typechecks
    ######################################################################

    def tc_If(self, node):
        condition_type = self.typecheck_child(node, 0)
        if condition_type != self.prims["boolean"]:
            raise TypecheckError(
                "At 'If', condition expected type is 'boolean' but got '{!s}'".format(condition_type))

        then_type = self.typecheck_child(node, 1)
        if then_type != self.prims["unit"]:
            raise TypecheckError("At 'If', then-block expected type is 'unit' but got '{!s}'".format(then_type))

        else_type = self.typecheck_child(node, 2)
        if else_type != self.prims["unit"]:
            raise TypecheckError(
                "At 'If', elseif statement expected type is 'unit' but got '{!s}'".format(else_type))

        return append_type(self.prims["unit"], node)

    def tc_ElseIf(self, node):
        if len(node.children) != 0:
            child_type = self.typecheck_child(node, 0)
            if child_type == self.prims["unit"]:
                return append_type(child_type, node)
            else:
                raise TypecheckError("At '{}', expected 'unit' but got '{!s}'".format(node.label, child_type))
        else:
            return append_type(self.prims["unit"], node)

    def tc_DeclExpr(self, node):
        if len(node.children) != 0:
            child_type = self.typecheck_child(node, 0)
            if child_type == self.prims["unit"]:
                return append_type(child_type, node)
            else:
                raise TypecheckError("At '{}', expected 'unit' but got '{!s}'".format(node.label, child_type))
        else:
            return append_type(self.prims["unit"], node)

    def tc_UpdateExpr(self, node):
        if len(node.children) != 0:
            child_type = self.typecheck_child(node, 0)
            if child_type == self.prims["unit"]:
                return append_type(child_type, node)
            else:
                raise TypecheckError("At '{}', expected 'unit' but got '{!s}'".format(node.label, child_type))
        else:
            return append_type(self.prims["unit"], node)

    def tc_BooleanExpr(self, node):
        child_type = self.typecheck_child(node, 0)
        if child_type == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError("At '{}', expected 'boolean' but got '{!s}'".format(node.label, child_type))

    def tc_For(self, node):
        self.push_scope()

        decl_type = self.typecheck_child(node, 0)
        if decl_type != self.prims["unit"]:
            raise TypecheckError("At 'For', expected type 'unit' for declaration but got '{!s}'".format(decl_type))

        bool_type = self.typecheck_child(node, 1)
        if bool_type != self.prims["boolean"]:
            raise TypecheckError("At 'For', expected type 'boolean' for condition but got '{!s}'".format(decl_type))

        update_type = self.typecheck_child(node, 2)
        if update_type != self.prims["unit"]:
            raise TypecheckError("At 'For', expected type 'unit' for update but got '{!s}'".format(decl_type))

        block_type = self.typecheck_child(node, 3)
        if block_type != self.prims["unit"]:
            raise TypecheckError("At 'For', expected type 'unit' for block but got '{!s}'".format(decl_type))

        self.pop_scope()
        return append_type(self.prims["unit"], node)

    # Call, Cast and helper typecheck
    ######################################################################

    def tc_Params(self, node):
        type_list = list()
        for child in node.children:
            type_list.append(self.typecheck_node(child))

        return append_typeList(tuple(type_list), node)

    def tc_Call(self, node):
        func_name = parse_node(node.children[0])[1]
        func_type = self.lookup_symbol(func_name)

        for t in self.num_types:
            if func_name == t.name:
                return self.tc_Cast(node, t)

        if func_type is not None and isinstance(func_type, FuncType):
            param_types = self.tc_Params(node.children[1])
            if param_types == func_type.params:
                append_type(func_type, node.children[0])
                return append_type(func_type.return_type, node)
            else:
                raise TypecheckError(
                    "Given parameters {!s} do not match parameters {!s} for function {}"
                    .format(param_types, func_type.params, func_name)
                )
        else:
            raise TypecheckError("Function '{}' is not defined in scope".format(func_name))

    def tc_Cast(self, node, num_type):
        if len(node.children[1].children) == 1:
            param_type = self.tc_Params(node.children[1])  # singleton tuple
            if param_type[0] in self.num_types:
                cast_func_type = FuncType(param_type, num_type)
                append_type(cast_func_type, node.children[0])
                node.label = "Cast"
                return append_type(num_type, node)
            else:
                raise TypecheckError("Cannot cast '{!s}' to '{!s}'".format(param_type[0], num_type))
        else:
            raise TypecheckError(
                "Cast '{!s}' requires one parameter but got {!s}"
                .format(num_type, len(node.children[1].children))
            )

    # Operators: Compare ops, Arith ops, Negate, Boolean ops
    ######################################################################

    def tc_Cmp(self, node):
        type1 = self.typecheck_child(node, 0)
        if type1 not in self.num_types:
            raise TypecheckError("Expected one of '{!s}' but got '{!s}'".format(self.num_types, type1))

        type2 = self.typecheck_child(node, 1)
        if type2 not in self.num_types:
            raise TypecheckError("Expected one of '{!s}' but got '{!s}'".format(self.num_types, type2))

        if type1 == type2:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError("Cannot compare '{!s}' to '{!s}'".format(type1, type2))

    def tc_ArithOp(self, node):
        type1 = self.typecheck_child(node, 0)
        if type1 not in self.num_types:
            raise TypecheckError("Expected one of '{!s}' but got '{!s}'".format(self.num_types, type1))

        type2 = self.typecheck_child(node, 1)
        if type2 not in self.num_types:
            raise TypecheckError("Expected one of '{!s}' but got '{!s}'".format(self.num_types, type2))

        if type1 == type2:
            return append_type(type1, node)
        else:
            raise TypecheckError(
                "Cannot perform operation '{}' on '{!s}' and '{!s}'".format(node.label, type1, type2))

    def tc_Negate(self, node):
        child_type = self.typecheck_node(node.children[0])
        if child_type in self.num_types:
            return append_type(child_type, node)
        else:
            raise TypecheckError("Expected one of '{!s}' but got '{!s}'".format(self.num_types, child_type))

    def tc_And(self, node):
        for child in node.children:
            child_type = self.typecheck_node(child)
            if child_type != self.prims["boolean"]:
                raise TypecheckError(
                    "At '{}', expected 'boolean' but got '{!s}'".format(node.label, child_type)
                )

        return append_type(self.prims["boolean"], node)

    def tc_Or(self, node):
        for child in node.children:
            child_type = self.typecheck_node(child)
            if child_type != self.prims["boolean"]:
                raise TypecheckError(
                    "At '{}', expected 'boolean' but got '{!s}'".format(node.label, child_type)
                )

        return append_type(self.prims["boolean"], node)

    def tc_Not(self, node):
        child_type = self.typecheck_child(node, 0)
        if child_type == self.prims["boolean"]:
            return append_type(self.prims["boolean"], node)
        else:
            raise TypecheckError("At '{}', expected 'boolean' but got '{!s}'".format(node.label, child_type))


class TypecheckError(Exception):
    """
    Class for errors during typing
    """
    pass


