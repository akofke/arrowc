#!/usr/bin/env python
# -*- coding: utf-8 -*-

from arrowc.arrowlang_parser import ArrowParser
from arrowc.arrowlang_typechecker import ArrowTypechecker
from arrowc.arrowlang_il.il_generator import ILGenerator
from nose.tools import raises
import re, string
import StringIO

def test_lexer_comments():
    assert str(ArrowParser().parse('''
    /*line comment \* escape sequences \/ \*/

    newlines
    end comment */
    var x = 0
    //line comment
    ''')) == '''
1:Stmts
2:ShortDecl
0:Name,x
0:Int,0
'''.strip()


def test_lexer_string():
    assert str(ArrowParser().parse('''
    var x = "a string with escaped \\" and \\\\"
    ''')) == '''
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
    assert str(ArrowParser().parse("var x = 0")) == '''
1:Stmts
2:ShortDecl
0:Name,x
0:Int,0
'''.strip()


#Nodes:AssignStmt
def test_parser2():
    assert str(ArrowParser().parse("x = 1")) == '''
1:Stmts
2:AssignStmt
0:Name,x
0:Int,1
'''.strip()


#Nodes:If, BooleanExpr, ==, Symbol, Block, ElseIf
def test_parser3():
    assert str(ArrowParser().parse("if x == 0 {y = 1} else {y = 0}")) == '''
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
    assert str(ArrowParser().parse("var x = 1 - 1.0")) == '''
1:Stmts
2:ShortDecl
0:Name,x
2:-
0:Int,1
0:Float,1.0
'''.strip()


#Nodes:+
def test_parser5():
    assert str(ArrowParser().parse("var x = 1 + 1")) == '''
1:Stmts
2:ShortDecl
0:Name,x
2:+
0:Int,1
0:Int,1
'''.strip()


#Nodes:Decl, Type, TypeName, *
def test_parser6():
    assert str(ArrowParser().parse("var x int32 = 1*1")) == '''
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
    assert str(ArrowParser().parse("func f (i int32) int32 { return 5}")) == '''
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
    assert str(ArrowParser().parse("print_int32(i)")) == '''
1:Stmts
2:Call
0:Symbol,print_int32
1:Params
0:Symbol,i
'''.strip()


#Nodes:For, DeclExpr, UpdateExpr, Continue
def test_parser9():
    assert str(ArrowParser().parse("for var i = 0; i < 20; i = i + 1 {print_int32(i) continue}")) == '''
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
    assert str(ArrowParser().parse("while(true){break}")) == '''
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


#Start of Typing tests
#A running list of every node created and type are listed. 

#Nodes:Stmts, call, symbol, Params, Int
#Types:Unit, int32
def test_checker1():
    assert str(ArrowTypechecker(ArrowParser().parse("print_int32(0)")).typecheck()) == '''
1:Stmts:unit
2:Call:unit
0:Symbol,print_int32:fn(int32)->unit
1:Params:(int32)
0:Int,0:int32
'''.strip()


#Nodes:ShortDecl, Name, Arith, Negate
def test_checker2():
    assert str(ArrowTypechecker(ArrowParser().parse("var x = 1 * 2 + 3 * (-1 + 7) / 2")).typecheck()) == '''
1:Stmts:unit
2:ShortDecl:unit
0:Name,x:int32
2:+:int32
2:*:int32
0:Int,1:int32
0:Int,2:int32
2:/:int32
2:*:int32
0:Int,3:int32
2:+:int32
1:Negate:int32
0:Int,1:int32
0:Int,7:int32
0:Int,2:int32
'''.strip()


#Nodes:Decl, Type, TypeName, Float
#Types:float32
def test_checker3():
    assert str(ArrowTypechecker(ArrowParser().parse("var x float32 = 1.0 * 2.0 + 3.0 * (-1.0 + 7.0) / 2.0")).typecheck()) == '''
1:Stmts:unit
3:Decl:unit
0:Name,x:float32
1:Type:float32
0:TypeName,float32:float32
2:+:float32
2:*:float32
0:Float,1.0:float32
0:Float,2.0:float32
2:/:float32
2:*:float32
0:Float,3.0:float32
2:+:float32
1:Negate:float32
0:Float,1.0:float32
0:Float,7.0:float32
0:Float,2.0:float32
'''.strip()


#Nodes:If, BooleanExpr, Boolean, ElseIf Block, AssignStmt, BooleanExpr
#Types:boolean
def test_checker4():
    assert str(ArrowTypechecker(ArrowParser().parse('''
var x = 0
if true {
  x = 1
} else {
  x = 2
}
''')).typecheck()) == """
2:Stmts:unit
2:ShortDecl:unit
0:Name,x:int32
0:Int,0:int32
3:If:unit
1:BooleanExpr:boolean
0:Boolean,true:boolean
1:Block:unit
2:AssignStmt:unit
0:Name,x:int32
0:Int,1:int32
1:ElseIf:unit
1:Block:unit
2:AssignStmt:unit
0:Name,x:int32
0:Int,2:int32
""".strip()


#Nodes:FuncDef, ParamsDecls, ParamDecl, ReturnType, Return, BlockStmt For, UpdateExpr, DeclExpr, cmp
def test_checker5():
    assert str(ArrowTypechecker(ArrowParser().parse('''
func fib(x int32) int32 {
  if x <= 0 {
    return 0
  }
  var prev = 0
  var cur = 1
  for var i = 1; i < x; i = i + 1 {
    var next = cur + prev
    prev = cur
    cur = next
  }
  return cur
}
print_int32(fib(10))
''')).typecheck()) == """
2:Stmts:unit
4:FuncDef:unit
0:Name,fib:fn(int32)->int32
1:ParamDecls:(int32)
2:ParamDecl:int32
0:Name,x:int32
1:Type:int32
0:TypeName,int32:int32
1:ReturnType:int32
1:Type:int32
0:TypeName,int32:int32
5:Block:unit
3:If:unit
1:BooleanExpr:boolean
2:<=:boolean
0:Symbol,x:int32
0:Int,0:int32
1:Block:unit
1:Return:unit
0:Int,0:int32
0:ElseIf:unit
2:ShortDecl:unit
0:Name,prev:int32
0:Int,0:int32
2:ShortDecl:unit
0:Name,cur:int32
0:Int,1:int32
4:For:unit
1:DeclExpr:unit
2:ShortDecl:unit
0:Name,i:int32
0:Int,1:int32
1:BooleanExpr:boolean
2:<:boolean
0:Symbol,i:int32
0:Symbol,x:int32
1:UpdateExpr:unit
2:AssignStmt:unit
0:Name,i:int32
2:+:int32
0:Symbol,i:int32
0:Int,1:int32
3:Block:unit
2:ShortDecl:unit
0:Name,next:int32
2:+:int32
0:Symbol,cur:int32
0:Symbol,prev:int32
2:AssignStmt:unit
0:Name,prev:int32
0:Symbol,cur:int32
2:AssignStmt:unit
0:Name,cur:int32
0:Symbol,next:int32
1:Return:unit
0:Symbol,cur:int32
2:Call:unit
0:Symbol,print_int32:fn(int32)->unit
1:Params:(int32)
2:Call:int32
0:Symbol,fib:fn(int32)->int32
1:Params:(int32)
0:Int,10:int32
""".strip()


#Types:function
def test_checker6():
    assert str(ArrowTypechecker(ArrowParser().parse("print_int32(0)")).typecheck()) == '''
1:Stmts:unit
2:Call:unit
0:Symbol,print_int32:fn(int32)->unit
1:Params:(int32)
0:Int,0:int32
'''.strip()


#Tests casting
def test_checker7():
    assert str(ArrowTypechecker(ArrowParser().parse("var x float32 = float32(1)")).typecheck()) == '''
1:Stmts:unit
3:Decl:unit
0:Name,x:float32
1:Type:float32
0:TypeName,float32:float32
2:Cast:float32
0:Symbol,float32:fn(int32)->float32
1:Params:(int32)
0:Int,1:int32
'''.strip()


def get_il(src):
    return ILGenerator(
        ArrowTypechecker(
            ArrowParser().parse(src)
        ).typecheck()
    ).get_prettyprint()

def sanitize_il(il):
    no_whitespace = re.sub("\s*", "", il)
    no_reg_numbers = re.sub("{\d+,\d+}", ",", no_whitespace)
    no_blk_numbers = re.sub("b-\d+", "b-", no_reg_numbers)
    return no_blk_numbers

#tests IL "CALL" function
#tests "IMM", "CALL", and "EXIT" operations
def test_ilgenerator1():
    file = open('test/testfiles/outputtest1.txt', 'r')
    outputstr = sanitize_il(get_il("print_int32(0)"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 

        
#tests IL "FOR", "Call", "AssignStmt", "LITERAL" "ArithOp" and "BOOLEANEXPR" functions
#Tests "J", "IFLT", "ADD" operations
def test_ilgenerator2():
    file = open('test/testfiles/outputtest2.txt', 'r')
    outputstr = sanitize_il(get_il("for var i = 0; i < 10; i = i + 1 { print_int32(i) }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 
  
#tests IL "FUNCDEF", both "CALL" functions, and the creation of a new block with "FUNCDEF"
#Tests "PRM", "MUL", "SUB", "RTRN" operations
def test_ilgenerator3():
    file = open('test/testfiles/outputtest3.txt', 'r')
    outputstr = sanitize_il(get_il("func f(i int32, j int32) int32 { return 5*j*j + - 3*j + 2*j*i + i + 7 } print_int32(f(2, 3))"))
    outputstr = re.sub("f-b-:label", "f:label", outputstr)
    booltester = True
    print outputstr
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
            print line
    assert booltester 
    
#tests the basic IL "ADDITION", "MULTIPLICATION", "DIVISION" function and the "NEGATING", "DECL", "EXPR" functions. 
#Tests "DIV" operation
def test_ilgenerator4():
    file = open('test/testfiles/outputtest4.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 1 * 2 + 3 * (-1 + 7) / 2"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 

#tests the use of parens to signify order
def test_ilgenerator5():
    file = open('test/testfiles/outputtest5.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 1.0 * 2.0 + 3.0 * (-1.0 + 7.0) / 2.0"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 

#tests if statement with else block, using true
def test_ilgenerator6():
    file = open('test/testfiles/outputtest6.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 0 if true { x = 1 } else { x = 2 }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester

#tests if statement with else block, using false
def test_ilgenerator7():
    file = open('test/testfiles/outputtest7.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 0 if false { x = 1 } else { x = 2 }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 

#tests if statement and the cmp function
#Tests "IFEQ"
def test_ilgenerator8():
    file = open('test/testfiles/outputtest8.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 0 if x == 0 { x = 1 } else { x = 2 }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 

#tests the use of different type float32
def test_ilgenerator9():
    file = open('test/testfiles/outputtest9.txt', 'r')
    outputstr = sanitize_il(get_il("var x float32 = 1.0 * 2.0 + 3.0 * (-1.0 + 7.0) / 2.0"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester

#tests the use casting
#Tests "CAST" op
def test_ilgenerator10():
    file = open('test/testfiles/outputtest12.txt', 'r')
    outputstr = sanitize_il(get_il("var x float32 = float32(1)"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester

#Tests "MOD" op
def test_ilgenerator11():
    file = open('test/testfiles/outputtest13.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 5 % 2"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester
    
#Tests for stmts
def test_ilgenerator12():
    file = open('test/testfiles/outputtest15.txt', 'r')
    outputstr = sanitize_il(get_il("for var i = 0; i < 10; i = i + 1 { print_int32(i) }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 
    
#Tests for And logic
def test_ilgenerator13():
    file = open('test/testfiles/outputtest16.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 0 if x >= 0 && x < 5 { x = 1 } else { x = 2 }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester 
    
#Tests Or logic
def test_ilgenerator14():
    file = open('test/testfiles/outputtest17.txt', 'r')
    outputstr = sanitize_il(get_il("var x = 0 if x >= 0 || x < 5 { x = 1 } else { x = 2 }"))
    booltester = True
    for line in file:
        if sanitize_il(line) not in outputstr:
            booltester = False
    assert booltester

# #Tests Call, Exit
# def x86_t1():
#     output = ("print_int32(0)")
#     assert output == 0
#
# #Tests addl, jmp, imm
# def x86_t2:
#     output = ("for var i = 0; i < 10; i = i + 1 { print_int32(i) }")
#     assert output == "0\n1\n2\n3\n4\n5\n6\n7\n8\n9"
#
#
# #Tests subl
# def x86_t3:
#     output = ("func f(i int32, j int32) int32 { return k - j } print_int32(f(2, 3))")
#     assert output == 1
#
# #tests imull
# def x86_t4:
#     output = ("func f(i int32, j int32) int32 { return j * k } print_int32(f(2, 3))")
#     assert output == 6
#
# #tests idivl
# def x86_t5:
#     output = ("var x = 2 / 1 + 3 * (-1 + 7) print_int32(x) ")
#     assert output == 20
#
# #tests cmpl, jmp
# def x86_t6:
#     output = ("var x = 0 if true { x = 1 } else { x = 2 } print_int32(x)")
#     assert output == 1
#
# def x86_t7:
#     output = ("var x = 0 if false { x = 1 } else { x = 2 } print_int32(x)")
#     assert output == 2
#
# def x86_t8:
#     output = ("var x = 0 if x >= 0 && x < 5 { x = 1 } else { x = 2 } print_int32(x)")
#     assert output == 1
#
# def x86_t9:
#     output = ("var x = 0 if x > 0 || x < 5 { x = 1 } else { x = 2 } print_int32(x)")
#     assert output == 1
#
# #tests divl functionality
# def x86_t10:
#     output = ("var x = 2 % 1 print_int32(x)")
#     assert output == 0