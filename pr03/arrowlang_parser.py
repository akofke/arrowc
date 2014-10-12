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
        p[0] = p[1].addkid(p[2])

    def p_Stmts2(self, p):
        'Stmts : TStmt'
        p[0] = Node("Stmts").addkid(p[1])

    # ##################################

    def p_TStmt(self, p):
        'TStmt : Stmt'
        p[0] = p[1]

    def p_TStmt2(self, p):
        'TStmt : FuncDefStmt'
        p[0] = p[1]

    ###################################

    def p_Stmt(self, p):
        'Stmt : CallStmt'
        p[0] = p[1]

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
        p[0] = p[2].addkid(p[3])

    def p_Block2(self, p):
        'Block : LBRACE BlockStmts RBRACE'
        p[0] = p[2]

    def p_Block3(self, p):
        'Block : LBRACE ReturnStmt RBRACE'
        p[0] = p[2]

    ###################################

    def p_BlockStmts(self, p):
        'BlockStmts : BlockStmts BlockStmt'
        p[0] = p[1].addkid(p[2])

    def p_BlockStmts2(self, p):
        'BlockStmts : BlockStmt'
        p[0] = Node("Block").addkid(p[1])

    ###################################

    def p_BlockStmt(self, p):
        'BlockStmt : Stmt'
        p[0] = p[1]

    def p_BlockStmt2(self, p):
        'BlockStmt : LoopControlStmt'
        p[0] = p[1]

    ###################################

    def p_Expr(self, p):
        'Expr : ArithExpr'
        p[0] = p[1]

    ###################################

    def p_FuncDefStmt(self, p):
        'FuncDefStmt : FUNC NAME LPAREN ParamDecls RPAREN TypeSpec Block'
        p[0] = Node("FuncDef") \
            .addkid(Node("Name," + p[2])) \
            .addkid(p[4]) \
            .addkid(Node("ReturnType").addkid(p[6])) \
            .addkid(p[7])

    def p_FuncDefStmt2(self, p):
        'FuncDefStmt : FUNC NAME LPAREN ParamDecls RPAREN Block'
        p[0] = Node("FuncDef") \
            .addkid(Node("Name," + p[2])) \
            .addkid(p[4]) \
            .addkid(Node("ReturnType")) \
            .addkid(p[6])

    def p_FuncDefStmt3(self, p):
        'FuncDefStmt : FUNC NAME LPAREN RPAREN TypeSpec Block'
        p[0] = Node("FuncDef") \
            .addkid(Node("Name," + p[2])) \
            .addkid(Node("ParamDecls")) \
            .addkid(Node("ReturnType").addkid(p[5])) \
            .addkid(p[6])

    def p_FuncDefStmt4(self, p):
        'FuncDefStmt : FUNC NAME LPAREN RPAREN Block'
        p[0] = Node("FuncDef") \
            .addkid(Node("Name," + p[2])) \
            .addkid(Node("ParamDecls")) \
            .addkid(Node("ReturnType")) \
            .addkid(p[5])

    ###################################

    def p_ParamDecls(self, p):
        'ParamDecls : ParamDecls COMMA NAME TypeSpec'
        p[0] = p[1].addKid(
            Node("ParamDecl").addkid(Node("Name," + p[2])).addkid(p[3])
        )

    def p_ParamDecls2(self, p):
        'ParamDecls : NAME TypeSpec'
        p[0] = Node("ParamDecls").addkid(
            Node("ParamDecl").addkid(Node("Name," + p[1])).addkid(p[2])
        )

    ###################################

    def p_BooleanExpr(self, p):
        'BooleanExpr : BooleanExpr OR OR AndExpr'
        p[0] = Node("Or").addkid(p[1]).addkid(p[3])


    def P_BooleanExpr2(self, p):
        'BooleanExpr : AndExpr'
        p[0] =  p[1]

    ###################################

    def p_AndExpr(self, p):
        'AndExpr : AndExpr AND AND NotExpr'

    def p_AndExpr2(self, p):
        'AndExpr : NotExpr'

    ###################################

    def p_NotExpr(self, p):
        'NotExpr : NOT BooleanTerm'

    def p_NotExpr2(self, p):
        'NotExpr : BooleanTerm'

    ###################################

    def p_BooleanTerm(self, p):
        'BooleanTerm : CmpExpr'

    def p_BooleanTerm2(self, p):
        'BooleanTerm : BooleanConstant'

    def p_BooleanTerm3(self, p):
        'BooleanTerm : LPAREN BooleanExpr RPAREN'

    ###################################

    def p_CmpExpr(self, p):
        'CompExpr : ArithExpr CmpOp ArithExpr'

    ###################################

    def p_CmpOp(self, p):
        'CmpOp : LT'
        p[0] = Node("<")

    def p_CmpOp2(self, p):
        'CmpOp : LT EQUALS'
        p[0] = Node("<=")

    def p_CmpOp3(self, p):
        'CmpOp : EQUALS EQUALS'
        p[0] = Node("==")

    def p_CmpOp4(self, p):
        'CmpOp : NOT EQUALS'
        p[0] = Node("!=")

    def p_CmpOp5(self, p):
        'CmpOp : GT EQUALS'
        p[0] = Node(">=")

    def p_CmpOp6(self, p):
        'CmpOp : GT'
        p[0] = Node(">")

    ###################################

    def p_BooleanConstant(self, p):
        'BooleanConstant : TRUE'
        p[0] = Node("True")

    def p_BooleanConstant2(self, p):
        'BooleanConstant : FALSE'
        p[0] = Node("False")

    ###################################

    def p_ArithExpr(self, p):
        'ArithExpr : ArithExpr PLUS MulDiv'

    def p_ArithExpr2(self, p):
        'ArithExpr : ArithExpr DASH MulDiv'

    def p_ArithExpr3(self, p):
        'ArithExpr : MulDiv'

    ###################################

    def p_MulDiv(self, p):
        'MulDiv : MulDiv STAR Negate'

    def p_MulDiv2(self, p):
        'MulDiv : MulDiv SLASH Negate'

    def p_MulDiv3(self, p):
        'MulDiv : MulDiv PERCENT Negate'

    def p_MulDiv4(self, p):
        'MulDiv : Negate'

    ###################################

    def p_Negate(self, p):
        'Negate : DASH Atomic'

    def p_MulDiv2(self, p):
        'Negate : Atomic'

    ###################################

    def p_Atomic(self, p):
        'Atomic : ValueExpr'

    def p_Atomic2(self, p):
        'Atomic : LPAREN ArithExpr RPAREN'

    ###################################

    def p_ValueExpr(self, p):
        'ValueExpr : Constant'

    def p_ValueExpr2(self, p):
        'ValueExpr : SymbolValueExpr'

    ###################################

    def p_Constant(self, p):
        'Constant : INT_CONST'

    def p_Constant2(self, p):
        'Constant : FLOAT_CONST'

    def p_Constant3(self, p):
        'Constant : STRING_CONST'

    ###################################

    def p_SymbolValueExpr(self, p):
        'SymbolValueExpr : Call'

    def p_SymbolValueExpr2(self, p):
        'SymbolValueExpr : NAME'

    ###################################

    def p_CallStmt(self, p):
        'CallStmt : Call'
        p[0] = p[1]

    ###################################

    def p_Call(self, p):
        'Call : NAME LPAREN CallParams RPAREN'
        p[0] = Node("Call").addkid(Node("Symbol," + p[1])).addkid(p[2])

    def p_Call2(self, p):
        'Call : NAME LPAREN RPAREN'
        p[0] = Node("Call").addkid(Node("Symbol," + p[1]))

    ###################################

    def p_CallParams(self, p):
        'CallParams : CallParams COMMA Expr'
        p[0] = p[1].addkid(p[3])

    def p_CallParams2(self, p):
        'CallParams : Expr'
        p[0] = Node("Params").addkid(p[1])


    ###################################

    def p_DeclStmt(self, p):
        'DeclStmt : VAR NAME TypeSpec EQUALS Expr'
        p[0] = Node("Decl")\
            .addkid(Node("Name," + p[2]))\
            .addkid(p[3])\
            .addkid(p[5])

    def p_DeclStmt2(self, p):
        'DeclStmt : VAR NAME TypeSpec'
        p[0] = Node("Decl").addkid(Node("Name," + p[2])).addkid(p[3])

    def p_DeclStmt3(self, p):
        'DeclStmt : VAR NAME EQUALS Expr'
        p[0] = Node("ShortDecl").addkid(Node("Name," + p[2])).addkid(p[3])

    ###################################

    def p_TypeName(self, p):
        'TypeName : NAME'
        p[0] = Node("TypeName," + p[1])

    ###################################

    def p_TypeSpec(self, p):
        'TypeSpec : TypeName'
        p[0] = Node("Type").addkid(p[1])

    ###################################

    def p_AssignStmt(self, p):
        'AssignStmt : NAME EQUALS Expr'
        p[0] = Node("AssignStmt")\
            .addkid(Node("Name," + p[1]))\
            .addkid(p[3])

    ###################################

    def p_IfStmt(self, p):
        'IfStmt : IF BooleanExpr Block ElseIfStmt'
        p[0] = Node("If")\
            .addkid(Node("BooleanExpr").addkid(p[2]))\
            .addkid(p[3])\
            .addkid(Node("ElseIf").addkid(p[4]))

    def p_IfStmt2(self, p):
        'IfStmt : IF BooleanExpr Block'
        p[0] = Node("If")\
            .addkid(Node("BooleanExpr").addkid(p[2]))\
            .addkid(p[3])\
            .addkid(Node("ElseIf"))

    ###################################

    def p_ElseIfStmt(self, p):
        'ElseIfStmt : ELSE Block'
        p[0] = p[2]

    def p_ElseIfStmt2(self, p):
        'ElseIfStmt : ELSE IfStmt'
        p[0] = p[2]

    ###################################

    def p_WhileStmt(self, p):
        'WhileStmt : WHILE BooleanExpr Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr"))\
            .addkid(Node("BooleanExpr").addkid(p[2]))\
            .addkid(Node("UpdateExpr"))\
            .addkid(p[3])

    def p_WhileStmt2(self, p):
        'WhileStmt : WHILE Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr"))\
            .addkid(Node("BooleanExpr"))\
            .addkid(Node("UpdateExpr"))\
            .addkid(p[3])

    ###################################

    def p_ForStmt(self, p):
        'ForStmt : FOR DeclStmt SEMIC BooleanExpr SEMIC AssignStmt Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr").addkid(p[2]))\
            .addkid(Node("BooleanExpr").addkid(p[4]))\
            .addkid(Node("UpdateExpr").addkid(p[6]))\
            .addkid(p[7])

    def p_ForStmt2(self, p):
        'ForStmt : FOR SEMIC BooleanExpr SEMIC AssignStmt Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr"))\
            .addkid(Node("BooleanExpr").addkid(p[3]))\
            .addkid(Node("UpdateExpr").addkid(p[5]))\
            .addkid(p[6])

    def p_ForStmt3(self, p):
        'ForStmt : FOR DeclStmt SEMIC SEMIC AssignStmt Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr").addkid(p[2]))\
            .addkid(Node("BooleanExpr"))\
            .addkid(Node("UpdateExpr").addkid(p[5]))\
            .addkid(p[6])

    def p_ForStmt4(self, p):
        'ForStmt : FOR DeclStmt SEMIC BooleanExpr SEMIC Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr").addkid(p[2]))\
            .addkid(Node("BooleanExpr").addkid(p[4]))\
            .addkid(Node("UpdateExpr"))\
            .addkid(p[6])

    def p_ForStmt5(self, p):
        'ForStmt : FOR SEMIC SEMIC AssignStmt Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr"))\
            .addkid(Node("BooleanExpr"))\
            .addkid(p[4])\
            .addkid(p[5])

    def p_ForStmt6(self, p):
        'ForStmt : FOR SEMIC BooleanExpr SEMIC Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr"))\
            .addkid(Node("BooleanExpr").addkid(p[3]))\
            .addkid(Node("UpdateExpr"))\
            .addkid(p[5])


    def p_ForStmt7(self, p):
        'ForStmt : FOR DeclStmt SEMIC SEMIC Block'
        p[0] = Node("For")\
            .addkid(Node("DeclExpr").addkid(p[2]))\
            .addkid(Node("BooleanExpr"))\
            .addkid((Node("UpdateExpr")))\
            .addkid(p[5])

    ###################################

    def p_ReutrnStmt(self, p):
        'ReturnStmt : RETURN'
        p[0] = Node("Return")

    def p_ReturnStmt2(self, p):
        'ReturnStmt : RETURN Expr'
        p[0] = Node("Return").addkid(p[2])

    ###################################

    def p_LoopControlStmt(self, p):
        'LoopControlStmt : CONTINUE'
        p[0] = Node("Continue")

    def p_LoopControlStmt2(self, p):
        'LoopControlStmt : BREAK'
        p[0] = Node("Break")