#!/usr/bin/env python
import re
import ply.lex as lex

#Reserved keywords
reserved = {
    'var': 'VAR',
    'func': 'FUNC',

    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'continue': 'CONTINUE',
    'break': 'BREAK',

    'true': 'TRUE',
    'false': 'FALSE',

    'return': 'RETURN'
}


class ArrowLexer(object):
    def __new__(cls, **kwargs):
        self = super(ArrowLexer, cls).__new__(cls, **kwargs)
        self.lexer = lex.lex(object=self, **kwargs)
        return self.lexer

    tokens = [
        # Identifier or keyword
        'NAME',

        # Int, float, and string literals
        'INT_CONST',
        'FLOAT_CONST',
        'STRING_CONST',

        # Assignment
        'EQUALS',

        # Operators
        'PLUS',
        'DASH',
        'STAR',
        'SLASH',
        'PERCENT',
        'LT',
        'GT',
        'AND',
        'OR',
        'NOT',

        # Delimeters
        'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET',
        'PERIOD', 'SEMIC', 'COMMA'
    ] + list(reserved.values())

    t_EQUALS = r'='

    t_PLUS = r'\+'
    t_DASH = r'-'
    t_STAR = r'\*'
    t_SLASH = r'/'
    t_PERCENT = r'%'
    t_LT = r'<'
    t_GT = r'>'
    t_AND = r'&'
    t_OR = r'\|'
    t_NOT = r'!'

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

    t_PERIOD = r'\.'
    t_SEMIC = r';'
    t_COMMA = r','

    def t_STRING_CONST(self, t):
        r'"(\\"|\\{2}|[^"])*?"'
        t.value = t.value.strip('\"')
        #t.value = re.sub(r'\\"', r'"', t.value) #leave escape characters for quotes since they need to be escaped later
        t.value = re.sub(r'\\{2}', r'\\', t.value)
        return t

    def t_NAME(self, t):
        r'([a-z]|[A-Z])([a-z]|[A-Z]|[0-9]|_)*'
        t.type = reserved.get(t.value, 'NAME')  # Check if it's a reserved word
        return t

    def t_NUM_CONST(self, t):
        r'[0-9]*\.?[0-9]+((E|e)(\+|-)?[0-9]+)?'
        try:
            t.value = int(t.value)
            t.type = 'INT_CONST'
            return t
        except ValueError:
            t.value = float(t.value)
            t.type = 'FLOAT_CONST'
            return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        pass

    def t_RANGE_COMMENT(self, t):
        r'/\*(\\\*/|\*\\/|.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass

    def t_LINE_COMMENT(self, t):
        r'//[^\n]*'
        t.lexer.lineno += 1
        pass

    t_ignore = ' \t'

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
