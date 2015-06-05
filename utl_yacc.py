#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import sys
import os
import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from utl_lex import tokens
from ast_node import ASTNode

AST = None
current_node = None


def p_utldoc(p):
    '''utldoc : assignment
              | assignment DOCUMENT'''
    print("value of '{}': {}".format(p[1], p[2]))


def p_assignment(p):
    '''assignment : ID ASSIGN expression'''
    p[1] = p[3]


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
    print("Syntax error in input!")


def do_parse(filename):
    """Open a file, parse it, return resulting parse."""
    parser = yacc.yacc()

    with open(filename, 'r') as utl_in:
        result = parser.parse(utl_in.read())

    return result


if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} utl_file\n".format(os.path.basename(sys.argv[0])))
        sys.stderr.write("       Parses a UTL file and outputs info for indexing.\n")
        sys.exit(1)

    print(do_parse(sys.argv[1]))
