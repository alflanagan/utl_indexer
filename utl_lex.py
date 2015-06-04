#!/usr/bin/env python3

import sys
import ply.lex as lex

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'elseif': 'ELSEIF',
    'then': 'THEN',
    'while': 'WHILE',
    'call': 'CALL',
    'macro': 'MACRO',
    'end': 'END',
    'return': 'RETURN',
    'exit': 'EXIT',
    'include': 'INCLUDE',
    'true': 'TRUE',
    'false': 'FALSE',
    'for': 'FOR',
    'continue': 'CONTINUE',
    'break': 'BREAK',
    'echo': 'ECHO',
    'default': 'DEFAULT',
    'as': 'AS',
    'foreach': 'FOR',
    # special variable names
    'this': 'THIS',
    'cms': 'CMS'
}

tokens = ['START_UTL',
          'END_UTL',
          'ID',
          'NUMBER',
          'COMMENT',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'COLON',
          'COMMA',
          'ASSIGN',
          'NULL',
          'MODULUS',
          'EQ',
          'NEQ',
          'AND',
          'OR',
          'NOT',
          'SEMI',
          'DOT',
          'RANGE',
          'FILTER',
          'STRING'] + list(set(reserved.values()))

t_START_UTL = r'\[%-?'
t_END_UTL = r'-?%]'

# "Identifier scoping is implemented only for macros. All other block
# constructs and included files operate in the same scope as the
# parent file. For macro scoping an identifier will first be sought
# for within the macro, and failing that the containing scope will be
# fallen back upon. A global scope exists and is accessible from all
# scoping levels (including exclusive). Global scope is normally used
# only for predefined filters and identifiers."


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # case-insensitive check for reserved words
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


# comment (ignore)
# PROBLEMS: comments *can* be nested
#          delimiters outside template ([% .. %])
#          should be ignored
def t_COMMENT(t):
    r'(/\*(.|\n)*?\*/)'
    pass


def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

literals = ['+', '-', '*', '/', '+=', '-=', '*=', '/=']
t_LPAREN = r'[)]'
t_RPAREN = r'[(]'
t_LBRACKET = r'\['
t_RBRACKET = r']'
t_COLON = r':'
t_COMMA = r','
t_ASSIGN = r'='
t_MODULUS = r'%|mod'
t_EQ = r'==|is'
t_NEQ = r'!=|is not'
t_AND = r'&&|and'
t_OR = r'\|\||or'
t_SEMI = r';'
t_DOT = r'\.'
t_NULL = r'null'
t_NOT = r'!|not'
t_RANGE = r'\.\.'
t_FILTER = r'\|'

string_re = r"'([^']*)'|" + r'"([^"]*)"'


# attributes of t param:
# t.type: the token type (as a string)
# t.value: the lexeme (the actual text matched)
# t.lineno: the current line number
# t.lexpos: the position of the token relative to the beginning of
#     the input text
# t.lexer: the Lexer object

# print attributes that are 'interesting' and not too long
# for x in dir(t.lexer):
#     # not method, special name
#     if (type(getattr(t.lexer, x)) != type(t.lexer.clone)
#             and not x.startswith('_')
#             and x not in ['lexdata', 'lexre', 'lexretext',
#                           'lexstaterenames', 'lexstateretext',
#                           'lextokens', 'lexstatere',
#                           'lextokens_all']):
#         print("{}: {}".format(x, getattr(t.lexer, x)))

def t_STRING(t):
    r'"(?P<dq>[^"]*)"|\'(?P<sq>[^\']*)\''
    dq = t.lexer.lexmatch.group('dq')
    sq = t.lexer.lexmatch.group('sq')
    t.value = dq if dq else sq
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'

lexer = lex.lex()
