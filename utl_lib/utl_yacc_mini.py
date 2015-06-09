#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc
import ply.lex as lex

from utl_lib.utl_lex import UTLLexer
from utl_lib.ast_node import ASTNode


# drastically simplified to aid debugging
class UTLParser(object):  # pylint: disable=too-many-public-methods
    """Represents the current state of parsing a UTL code source, and generated AST."""

    def __init__(self):
        self.current_node = None
        self.symbol_table = {}
        self.parsed = False
        self.documents = []
        "Contents of each document (i.e. non-UTL) section."
        self.tokens = UTLLexer.tokens
        self.parser = yacc.yacc(module=self)

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
    )

    def parse(self, input_text=None, lexer=None, debug=False, tracking=False, tokenfunc=None):
        """Parses the code in `input_text`, returns result.

        lexer defaults to the `lexer` of a new instance of
        :py:class:`~utl_lib.utl_lex.UTLLexer`.

        """
        this_lexer = lexer if lexer else UTLLexer().lexer
        return self.parser.parse(input_text, this_lexer, debug, tracking, tokenfunc)

    def p_utldoc(self, p):  # pylint: disable=unused-argument
        '''utldoc : document_or_code
                  | utldoc document_or_code'''
        self.parsed = True
        p[0] = ASTNode('root')

    def p_document_or_code(self, p):
        '''document_or_code : document
                            | START_UTL statement_list END_UTL'''
        # attributes of p:
        # error, lexer, lexpos, lexspan, lineno, linespan, parser, set_lineno, slice, stack
        pass

    def p_document(self, p):
        '''document : DOCUMENT'''
        self.documents.append(p[1])
        pass

    def p_statement_list(self, p):
        '''statement_list : statement_list SEMI statement SEMI
                          | statement SEMI'''
        pass

    def p_statement(self, p):
        '''statement : expr SEMI
                     | assignment SEMI'''
        pass

    def p_expr_array_ref(self, p):
        '''expr : expr PLUS term
                | expr MINUS term
                | term
                | FILTER method_call
                '''
        if isinstance(p[1], float):
            p[0] = p[1]
        elif p[1] in self.symbol_table:
            p[0] = self.symbol_table[p[1]]


    # convenience rule to explicitly state production to nothing
    def p_empty(self, p):
        '''empty :'''
        pass


    def p_param_list(self, p):
        '''param_list : param_decl
                      | param_decl COMMA param_list
                      | empty'''
        pass

    def p_param_decl(self, p):
        '''param_decl : ID
                      | assignment'''
        pass

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expr'''
        self.symbol_table[p[1]] = p[3]

    def p_method_call(self, p):
        '''method_call : ID
                       | ID RPAREN param_list LPAREN'''
        pass

    def p_term(self, p):
        '''term : term TIMES factor
                | term DIV factor
                | term MODULUS factor
                | factor'''
        if len(p) == 3:
            pass
        else:
            p[0] = p[1]

    def p_factor(self, p):
        '''factor : NUMBER
                  | LPAREN expr RPAREN
                  | ID LBRACKET expr RBRACKET
                  | ID'''
        if isinstance(p[1], float):
            p[0] = p[1]  # NUMBER
        elif p[1].type == 'LPAREN':
            p[0] = p[2]
        elif p[1] in self.symbol_table:
            p[0] = self.symbol_table[p[1]]
        else:
            p[0] = '*not found*'


    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        badline = p.lexer.lexdata.split('\n')[p.lineno-1]
        print("Syntax error in input line {} at '{}'!".format(p.lineno, p.value))
        print(badline)
