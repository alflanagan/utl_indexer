#!/usr/bin/env python3

import sys
import ply.lex as lex

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'call': 'CALL',
    'macro': 'MACRO',
    'end': 'END',
    'return': 'RETURN',
}

tokens = ['START_UTL',
          'END_UTL',
          'ID',
          'NUMBER',
          'COMMENT_START',
          'COMMENT_END',
          'COMMENT',
          'RPAREN',
          'LPAREN',
          'COLON',
          'COMMA',
          'ASSIGN',
          'MODULUS',
          'EQ',
          'NEQ',
          'AND',
          'OR',
          'SEMI',
          'DOT',
          'STRING'] + list(reserved.values())


t_START_UTL = r'\[%-?'
t_END_UTL = r'-?%]'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    return t

in_comment = False


def t_COMMENT_START(t):
    r'/\*'
    global in_comment
    in_comment = True
    pass


def t_COMMENT_END(t):
    r'\*/'
    global in_comment
    in_comment = False
    pass


def t_COMMENT(t):
    r'/\*.*\*/'
    pass


def t_NUMBER(t):
    r'\d+(\.\d*)?'
    t.value = float(t.value)
    return t

literals = ['+', '-', '*', '/']
t_RPAREN = r'[(]'
t_LPAREN = r'[)]'
t_COLON = r':'
t_COMMA = r','
t_ASSIGN = r'='
t_MODULUS = r'%'
t_EQ = r'=='
t_NEQ = r'!='
t_AND = r'&&'
t_OR = r'\|\|'
t_SEMI = r';'
t_DOT = r'\.'

string_re = r"'([^']*)'|" + r'"([^"]*)"'


def t_STRING(t):
    r'\'([^\']*)\'|"([^"]*)"'
    # t.type: the token type (as a string), t.value: the lexeme (the
    # actual text matched), t.lineno: the current line number, and
    # t.lexpos: the position of the token relative to the beginning of
    # the input text, t.lexer: the Lexer object that produced the
    # token

    # t.lexer has: begin(), clone(), current_state(), input(),
    # lexdata, lexeoff, lexerrorf(), lexignore, lexlen, lexliterals,
    # lexmatch, lexmodule, lexoptimize, lexpos, lexre, lexreflags,
    # lexretext, lexstate, lexstateeoff, lexstateerrorf,
    # lexstateignore, lexstateinfo, lexstatere, lexstaterenames,
    # lexstateretext, lexstatestack, lextokens, lextokens_all, lineno,
    # next(), pop_state(), push_state(), readtab(), skip(), token(),
    # writetab()

    # print attributes that are 'interesting' and not too long
    # for x in dir(t.lexer):
    #     if (type(getattr(t.lexer, x)) != type(t.lexer.clone)
    #             and not x.startswith('_')
    #             and x not in ['lexdata', 'lexre', 'lexretext',
    #                           'lexstaterenames', 'lexstateretext',
    #                           'lextokens', 'lexstatere',
    #                           'lextokens_all']):

    #         print("{}: {}".format(x, getattr(t.lexer, x)))

    # don't entirely understand how it's doing the match object
    # but we want the second match that's not None
    first_match = None
    for str in t.lexer.lexmatch.groups():
        if str and first_match:
            t.value = str
            break
        elif str:
            first_match = str
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
