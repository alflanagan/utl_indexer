#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from utl_lib.utl_lex import UTLLexer

current_node = None
symbol_table = {}

# grammar for UTL sections. loosely based on PHP grammar
# http://lxr.php.net/xref/PHP_TRUNK/Zend/zend_language_parser.y

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIV', 'MODULUS'),
)

def p_utldoc(p):
    '''utldoc : document_or_code
              | utldoc document_or_code'''
    print('utldoc')

def p_document_or_code(p):
    '''document_or_code : DOCUMENT
                        | START_UTL top_statement END_UTL'''
    print('document_or_code')

def p_top_statement(p):
    '''top_statement : statement
                     | macro_declaration_statement
                     | ID'''
    pass

def p_statement(p):
    '''statement : if_stmt
                 | WHILE LPAREN expr RPAREN statement_list END optional_semi
                 | for_stmt
                 | array_decl
                 | BREAK optional_expr optional_semi
                 | CONTINUE optional_expr optional_semi
                 | ECHO echo_expr_list optional_semi
                 | expr optional_semi
                 | SEMI
                 | COMMENT
                 | include_stmt
                 | assignment
                 | CALL method_call
                 | RETURN optional_expr optional_semi
                 | EXIT
                 | empty
                 '''
    pass

def p_array_decl(p):
    '''array_decl : ID LBRACKET values_list RBRACKET'''
    pass

def p_values_list(p):
    '''values_list : values_list COMMA expr
                   | values_list COMMA ID COLON expr
                   | empty'''
    pass

def p_expr_array_ref(p):
    '''expr : ID LBRACKET expr RBRACKET'''
    pass

def p_for_for(p):
    '''for_for : FOR
               | FOR EACH'''
    pass

def p_for_stmt(p):
    '''for_stmt : for_for expr
                | for_for expr AS ID
                | for_for expr AS ID COMMA ID'''
    pass

def p_echo_expr_list(p):
    '''echo_expr_list : echo_expr_list COMMA echo_expr
                      | echo_expr'''
    pass

def p_echo_expr(p):
    '''echo_expr : expr'''
    pass

def p_optional_expr(p):
    '''optional_expr : empty
                     | expr'''
    pass

def p_simple_if_stmt(p):
    '''simple_if_stmt : IF LPAREN expr RPAREN statement_list END optional_semi'''
    pass

def p_if_stmt_elseif(p):
    '''if_stmt_elseif : simple_if_stmt
                      | if_stmt_elseif ELSEIF LPAREN expr RPAREN statement_list END optional_semi'''
    pass

def p_if_stmt(p):
    '''if_stmt : if_stmt_elseif
               | if_stmt_elseif ELSE statement_list END optional_semi
               | IF expr THEN statement'''
    pass

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    pass

def p_optional_semi(p):
    '''optional_semi : SEMI
                     | empty'''
    pass

# convenience rule to explicitly state production to nothing
def p_empty(p):
    '''empty :'''
    pass


def p_macro_declaration_statement(p):
    '''macro_declaration_statement : MACRO ID LPAREN param_list RPAREN statement_list END
                                   | MACRO ID statement_list END'''
    pass

def p_param_list(p):
    '''param_list : param_decl
                  | param_decl COMMA param_list
                  | '''
    pass

def p_param_decl(p):
    '''param_decl : ID
                  | assignment'''
    print('param_decl')

def p_assignment(p):
    '''assignment : ID ASSIGN expr
                  | ID ASSIGNOP expr
                  | DEFAULT ASSIGN expr'''
    symbol_table[p[1]] = p[3]

def p_expr_op(p):
    '''expr : expr OP expr'''
    print("Found unhandled operator: {}".format(p[2].value))

def p_expr_plus(p):
    '''expr : expr PLUS term'''
    p[0] = p[1] + p[3]


def p_expr_minus(p):
    '''expr : expr MINUS term'''
    p[0] = p[1] - p[3]

def p_expr_term(p):
    '''expr : term'''
    p[0] = p[1]

def p_expr_null(p):
    '''expr : NULL'''
    p[0] = None

def p_expr_true(p):
    '''expr : TRUE'''
    p[0] = True

def p_expr_false(p):
    '''expr : FALSE'''
    p[0] = False

def p_expr_range(p):
    '''expr : expr RANGE expr'''
    pass

def p_expr_filter(p):
    '''expr : expr FILTER method_call'''
    pass

def p_method_call(p):
    '''method_call : ID
                   | ID RPAREN param_list LPAREN'''
    pass

def p_term_times(p):
    '''term : term TIMES factor'''
    p[0] = p[1] * p[3]


def p_term_div(p):
    'term : term DIV factor'
    p[0] = p[1] / p[3]


def p_term_mod(p):
    '''term : term MODULUS factor'''
    pass

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expr RPAREN'
    p[0] = p[2]

def p_include(p):
    '''include_stmt : INCLUDE STRING'''
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

