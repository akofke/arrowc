#!/usr/bin/env python
# -*- coding: utf-8 -*-

from betterast import Node
from ply import yacc
from arrowlang_lexer import ArrowLexer

class ArrowParser(object):
    def build(self, **kwargs):
        self.yacc = yacc.yacc(module=self, **kwargs)

    tokens = ArrowLexer.tokens

    def p_Start(self, p):
        'Start : Stmts'
        p[0] = p[1]

    def p_Stmts(self, p):
        'Stmts : Stmts TStmt'
        p[0] = p[1].addKid(p[2])

    def p_Stmts2(self, p):
        'Stmts : TStmt'
        p[0] = Node("Stmt").addkid(p[1])

    def p_TStmt(self, p):
        'TStmt : Stmt'
        p[0] = p[1]

    def p_TStmt2(self, p):
        'TStmt : FuncDefStmt'
        p[0] = Node("FuncDef").addKid(p[1])

    def p_Stmt(self, p):
        'Stmt : CallStmt'


