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

      def p_Block2(self, p):
        'Block : LBRACE BlockStmts RBRACE'

    def p_Block3(self, p):
        'Block : LBRACE BlockStmts RBRACE'

    ###################################

    def p_BlockStmts(self, p):
        'BlockStmts : BlockStmts BlockStmt'

    def p_BlockStmts2(self, p):
        'BlockStmts : BlockStmt'

    ###################################

    def p_BlockStmt(self, p):
        'BlockStmt : Stmt'

    def p_BlockStmt2(self, p):
        'BlockStmt : LoopControlStmt'

    ###################################

    def p_Expr(self, p):
        'Expr : ArithExpr'

    ###################################

    def p_FuncDefStmt(self, p):
        'FuncDefStmt : func NAME "(" ParamDecls ")" TypeSpec Block'

    def p_FuncDefStmt2(self, p):
        'FuncDefStmt : func NAME "(" ParamDecls ")" Block'

    def p_FuncDefStmt3(self, p):
        'FuncDefStmt : func NAME "(" ")" TypeSpec Block'

    def p_FuncDefStmt4(self, p):
        'FuncDefStmt : func NAME "(" ")" Block'

    ###################################

    def p_ParamDecls(self, p):
        'ParamDecls : ParamDecls "," NAME TypeSpec'

    def p_ParamDecls2(self, p):
        'ParamDecls : NAME TypeSpec'

    ###################################

    def p_BooleanExpr(self, p):
        'BooleanExpr : BooleanExpr "|" "|" AndExpr'

    def P_BooleanExpr2(self, p):
        'BooleanExpr : AndExpr'

    ###################################

    def p_AndExpr(self, p):
        'AndExpr : AndExpr "&" "&" NotExpr'

    def AndExpr2(self, p):
        'AndExpr : NotExpr'

    ###################################

    def p_NotExpr(self, p):
        'NotExpr : "!" BooleanTerm'

    def NotExpr2(self, p):
        'NotExpr : BooleanTerm'

    ###################################

    def p_BooleanTerm(self, p):
        'BooleanTerm : CmpExpr'

    def p_BooleanTerm2(self, p):
        'BooleanTerm : BooleanConstant'

    def p_BooleanTerm3(self, p):
        'BooleanTerm : "(" BooleanExpr ")"'

    ###################################

    def p_CmpExpr(self, p):
        'ArithExpr CmpOp ArithExpr'

    ###################################

    def p_CmpOp(self, p):
        'CmpOp : "<"'

    def p_CmpOp2(self, p):
        'CmpOp : "<" "="'

    def p_CmpOp3(self, p):
        'CmpOp : "=" "="'

    def p_CmpOp4(self, p):
        'CmpOp : "!" "="'

    def p_CmpOp5(self, p):
        'CmpOp : ">" "="'

    def p_CmpOp6(self, p):
        'CmpOp : ">"'

    ###################################

    def p_BooleanConstant(self, p):
        'BooleanConstant : true'

    def p_BooleanConstant2(self, p):
        'BooleanConstant : false'

    ###################################

    def p_ArithExpr(self, p):
        'ArithExpr : ArithExpr "+" MulDiv'

    def p_ArithExpr2(self, p):
        'ArithExpr : ArithExpr "-" MulDiv'

    def p_ArithExpr3(self, p):
        'ArithExpr : MulDiv'

    ###################################

    def p_MulDiv(self, p):
        'MulDiv : MulDiv "*" Negate'

    def p_MulDiv2(self, p):
        'MulDiv : MulDiv "/" Negate'

    def p_MulDiv3(self, p):
        'MulDiv : MulDiv "%" Negate'

    def p_MulDiv4(self, p):
        'MulDiv : Negate'

    ###################################

    def p_Negate(self, p):
        'Negate : "-" Atomic'

    def p_MulDiv2(self, p):
        'Negate : Atomic'

    ###################################

    def p_Atomic(self, p):
        'Atomic : ValueExpr'

    def p_Atomic2(self, p):
        'Atomic : "(" ArithExpr ")"'


