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
        p[0] = Node("Stmts").addkid(p[1])

    def p_Stmts(self, p):
        'Stmts : Stmts TStmt'
        p[0] = p[1].addkid(p[2])

    def p_Stmts2(self, p):
        'Stmts : TStmt'
        p[0] = p[1]

    ###################################

    def p_TStmt(self, p):
        'TStmt : Stmt'
        p[0] = p[1]

    def p_TStmt2(self, p):
        'TStmt : FuncDefStmt'
        p[0] = Node("FuncDef").addkid(p[1])

    ###################################

    def p_Stmt(self, p):
        'Stmt : CallStmt'
        p[0] = Node("")

    def p_Stmt2(self, p):
        'Stmt : DeclStmt'
        p[0] = p[1]

    def p_Stmt3(self, p):
        'Stmt : AssignStmt'
        p[0] = p[1]

    def p_Stmt4(self, p):
        'Stmt : IfStmt'
        p[0] = p[1]

    def p_Stmt5(self, p):
        'Stmt : WhileStmt'
        p[0] = p[1]
        
    def p_Stmt6(self, p):
        'Stmt : ForStmt'
        p[0] = p[1]

    ###################################

    def p_Block(self, p):
        'Block : LBRACE BlockStmts ReturnStmt RBRACE'


