#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from utl_lib.utl_lex import UTLLexer

current_node = None
symbol_table = {}


def p_utldoc(p):
    '''utldoc :
              | utldoc document_or_code'''
    print('utldoc')

def p_document_or_code(p):
    '''document_or_code : DOCUMENT
                        | START_UTL assignment END_UTL'''
    print('document_or_code')

# def p_statement(p):
    # '''statement : assignment
                 # | declaration'''
    # print('statement')

# def p_declaration(p):
    # '''declaration : MACRO ID LPAREN param_list RPAREN statements END
                   # | MACRO ID SEMI statements END'''

# def p_param_list(p):
    # '''param_list : param_decl
                  # | param_decl COMMA param_list
                  # | '''

# def p_param_decl(p):
    # '''param_decl : ID
                  # | ID ASSIGN expression'''
    # print('param_decl')

def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    symbol_table[p[1]] = p[3]


def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


def p_term_div(p):
    'term : term DIV factor'
    p[0] = p[1] / p[3]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    badline = p.lexer.lexdata.split('\n')[p.lineno-1]
    print("Syntax error in input line!")
    print(badline)
    print("{}^".format(' ' * (p.lexpos - 1)))



def parser():
    tokens = UTLLexer.tokens
    return yacc.yacc()

