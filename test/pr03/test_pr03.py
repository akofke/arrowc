#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Put your test code for pr03 here '''

import pr03
from pr03.arrowlang_parser import ArrowParser
from pr03.arrowlang_lexer import ArrowLexer
from nose.tools import raises


def test_lexer_comments():
    assert str(ArrowParser().parse('''
    /*line comment \* escape sequences \/ \*/

    newlines
    end comment */
    var x = 0
    //line comment
    ''', lexer=ArrowLexer())) == '''
1:Stmts
2:ShortDecl
0:Name,x
0:Int,0
'''.strip()


def test_lexer_string():
    assert str(ArrowParser().parse('''
    var x = "a string with escaped \\" and \\\\"
    ''', lexer=ArrowLexer())) == '''
1:Stmts
2:ShortDecl
0:Name,x
0:String,a string with escaped \\" and \\
'''.strip()
#The actual output should contain the sequences \" and \


#The following parser tests implement every node call that could be created.
#A running list of each node will be stated for each test, identifying the 
#additional nodes that had not yet been tested

#Nodes:Stmts, ShortDecl, Name, Int
def test_parser1():
    assert str(ArrowParser().parse("var x = 0", lexer=ArrowLexer())) == '''
1:Stmts
2:ShortDecl
0:Name,x
0:Int,0
'''.strip()


#Nodes:AssignStmt
def test_parser2():
    assert str(ArrowParser().parse("x = 1", lexer=ArrowLexer())) == '''
1:Stmts
2:AssignStmt
0:Name,x
0:Int,1
'''.strip()


#Nodes:If, BooleanExpr, ==, Symbol, Block, ElseIf
def test_parser3():
    assert str(ArrowParser().parse("if x == 0 {y = 1} else {y = 0}", lexer=ArrowLexer())) == '''
1:Stmts
3:If
1:BooleanExpr
2:==
0:Symbol,x
0:Int,0
1:Block
2:AssignStmt
0:Name,y
0:Int,1
1:ElseIf
1:Block
2:AssignStmt
0:Name,y
0:Int,0
'''.strip()


#Nodes:-, Float
def test_parser4():
    assert str(ArrowParser().parse("var x = 1 - 1.0", lexer=ArrowLexer())) == '''
1:Stmts
2:ShortDecl
0:Name,x
2:-
0:Int,1
0:Float,1.0
'''.strip()


#Nodes:+
def test_parser5():
    assert str(ArrowParser().parse("var x = 1 + 1", lexer=ArrowLexer())) == '''
1:Stmts
2:ShortDecl
0:Name,x
2:+
0:Int,1
0:Int,1
'''.strip()


#Nodes:Decl, Type, TypeName, *
def test_parser6():
    assert str(ArrowParser().parse("var x int32 = 1*1", lexer=ArrowLexer())) == '''
1:Stmts
3:Decl
0:Name,x
1:Type
0:TypeName,int32
2:*
0:Int,1
0:Int,1
'''.strip()


#Nodes:FuncDef, ParamDecls, ParamDecl, ReturnType, Return
def test_parser7():
    assert str(ArrowParser().parse("func f (i int32) int32 { return 5}", lexer=ArrowLexer())) == '''
1:Stmts
4:FuncDef
0:Name,f
1:ParamDecls
2:ParamDecl
0:Name,i
1:Type
0:TypeName,int32
1:ReturnType
1:Type
0:TypeName,int32
1:Block
1:Return
0:Int,5
'''.strip()


#Nodes:Call, Params
def test_parser8():
    assert str(ArrowParser().parse("print_int32(i)", lexer=ArrowLexer())) == '''
1:Stmts
2:Call
0:Symbol,print_int32
1:Params
0:Symbol,i
'''.strip()


#Nodes:For, DeclExpr, UpdateExpr, Continue
def test_parser9():
    assert str(ArrowParser().parse("for var i = 0; i < 20; i = i + 1 {print_int32(i) continue}", lexer=ArrowLexer())) == '''
1:Stmts
4:For
1:DeclExpr
2:ShortDecl
0:Name,i
0:Int,0
1:BooleanExpr
2:<
0:Symbol,i
0:Int,20
1:UpdateExpr
2:AssignStmt
0:Name,i
2:+
0:Symbol,i
0:Int,1
2:Block
2:Call
0:Symbol,print_int32
1:Params
0:Symbol,i
0:Continue
'''.strip()


#Nodes:While,Break
def test_parser10():
    assert str(ArrowParser().parse("while(true){break}", lexer=ArrowLexer())) == '''
1:Stmts
4:For
0:DeclExpr
1:BooleanExpr
0:Boolean,true
0:UpdateExpr
1:Block
0:Break
'''.strip()


#Large overall test
def test_parser11():
    assert str(ArrowParser().parse('''
var x = 1
var x = 2
func foo() { return }
func bar() { return }
func baz() { return }
if x == y && (y == z || z == c) {
    foo()
} else if (y < z) || (z > x && x != y) {
    bar()
} else {
    baz()
}''')) == """
6:Stmts
2:ShortDecl
0:Name,x
0:Int,1
2:ShortDecl
0:Name,x
0:Int,2
4:FuncDef
0:Name,foo
0:ParamDecls
1:ReturnType
1:Type
0:TypeName,unit
1:Block
0:Return
4:FuncDef
0:Name,bar
0:ParamDecls
1:ReturnType
1:Type
0:TypeName,unit
1:Block
0:Return
4:FuncDef
0:Name,baz
0:ParamDecls
1:ReturnType
1:Type
0:TypeName,unit
1:Block
0:Return
3:If
1:BooleanExpr
2:And
2:==
0:Symbol,x
0:Symbol,y
2:Or
2:==
0:Symbol,y
0:Symbol,z
2:==
0:Symbol,z
0:Symbol,c
1:Block
2:Call
0:Symbol,foo
0:Params
1:ElseIf
3:If
1:BooleanExpr
2:Or
2:<
0:Symbol,y
0:Symbol,z
2:And
2:>
0:Symbol,z
0:Symbol,x
2:!=
0:Symbol,x
0:Symbol,y
1:Block
2:Call
0:Symbol,bar
0:Params
1:ElseIf
1:Block
2:Call
0:Symbol,baz
0:Params
""".strip()
