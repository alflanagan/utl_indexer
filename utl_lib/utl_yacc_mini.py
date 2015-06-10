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
        '''utldoc : utldoc document_or_code
                  | document_or_code'''
        self.parsed = True
        if len(p) == 2:
            # p[1] is 'statement_list'
            p[0] =  ASTNode('root', False, {}, [p[1]])
        else:
            # p[1] is 'root'
            p[1].add_children(p[2:])
            p[0] = p[1]

    def p_document_or_code(self, p):
        '''document_or_code : DOCUMENT
                            | START_UTL statement_list END_UTL'''
        # attributes of p:
        # error, lexer, lexpos, lexspan, lineno, linespan, parser, set_lineno, slice, stack
        if len(p) == 2:
            newnode = ASTNode('document', True, {'text': p[1]})
        else:
            newnode = p[2]
        p[0] = newnode

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | statement'''
        p[0] = ASTNode('statement_list', False, {}, p[1:])

    def p_statement(self, p):
        '''statement : expr SEMI
                     | assignment SEMI'''
        p[0] = ASTNode('statement', False, {}, [p[1]])

    def p_expr(self, p):
        '''expr : expr PLUS term
                | expr MINUS term
                | term
                | FILTER method_call

                '''
        p[0] = ASTNode('expr', False)

    # convenience rule to explicitly state production to nothing
    def p_empty(self, p):
        '''empty :'''
        pass

    def p_param_list(self, p):
        '''param_list : param_decl
                      | param_list COMMA param_decl
                      | empty'''
        pass

    def p_param_decl(self, p):
        '''param_decl : ID
                      | assignment'''
        pass

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expr'''
        p[0] = ASTNode('assignment', False)

    def p_method_call(self, p):
        '''method_call : ID LPAREN param_list RPAREN'''
        pass

    def p_term(self, p):
        '''term : term TIMES factor
                | term DIV factor
                | term MODULUS factor
                | factor'''
        pass

    def p_factor(self, p):
        '''factor : NUMBER
                  | ID LBRACKET expr RBRACKET
                  | ID
                  | LPAREN expr RPAREN
                  | method_call'''
        pass

    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        badline = p.lexer.lexdata.split('\n')[p.lineno-1]
        lineoffset = p.lexer.lexdata.rfind('\n', 0, p.lexer.lexpos)
        if lineoffset == -1:  # we're on first line
            lineoffset = 0
        lineoffset = p.lexer.lexpos - lineoffset
        print("Syntax error in input line {} after '{}'!".format(p.lineno, p.value))
        print(badline)
        print("{}^".format(' ' * (lineoffset - 1)))
