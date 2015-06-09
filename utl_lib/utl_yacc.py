#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc
import ply.lex as lex

from utl_lib.utl_lex import UTLLexer
from utl_lib.ast_node import ASTNode



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

# grammar for UTL sections. loosely based on PHP grammar
# http://lxr.php.net/xref/PHP_TRUNK/Zend/zend_language_parser.y
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
        self.asts.append(ASTNode('utldoc'))

    def p_document_or_code(self, p):
        '''document_or_code : document
                            | START_UTL top_statement END_UTL'''
        # attributes of p:
        # error, lexer, lexpos, lexspan, lineno, linespan, parser, set_lineno, slice, stack
        self.asts.append(ASTNode('document_or_code'))

    def p_document(self, p):
        '''document : DOCUMENT'''
        self.documents.append(p.lexspan)
        self.asts.append(ASTNode('document[{}]'.format(len(self.documents) - 1)))

    def p_top_statement(self, p):
        '''top_statement : statement SEMI
                         | macro_declaration_statement SEMI
                         | ID SEMI
                         | top_statement SEMI top_statement'''
        pass

    def p_statement(self, p):
        '''statement : if_stmt
                     | WHILE LPAREN expr RPAREN statement_list END SEMI
                     | for_stmt
                     | array_decl
                     | BREAK optional_expr SEMI
                     | CONTINUE optional_expr SEMI
                     | ECHO echo_expr_list SEMI
                     | expr SEMI
                     | SEMI
                     | COMMENT
                     | include_stmt SEMI
                     | assignment SEMI
                     | CALL method_call SEMI
                     | RETURN optional_expr SEMI
                     | EXIT
                     '''
        pass

    def p_array_decl(self, p):
        '''array_decl : ID LBRACKET values_list RBRACKET'''
        pass

    def p_values_list(self, p):
        '''values_list : values_list COMMA expr
                       | values_list COMMA ID COLON expr
                       | empty'''
        pass

    def p_expr_array_ref(self, p):
        '''expr : ID LBRACKET expr RBRACKET'''
        pass

    def p_for_for(self, p):
        '''for_for : FOR
                   | FOR EACH'''
        pass

    def p_for_stmt(self, p):
        '''for_stmt : for_for expr SEMI
                    | for_for expr AS ID SEMI
                    | for_for expr AS ID COMMA ID SEMI'''
        pass

    def p_echo_expr_list(self, p):
        '''echo_expr_list : echo_expr_list COMMA echo_expr
                          | echo_expr'''
        pass

    def p_echo_expr(self, p):
        '''echo_expr : expr'''
        pass

    def p_optional_expr(self, p):
        '''optional_expr : empty
                         | expr'''
        pass

    def p_simple_if_stmt(self, p):
        '''simple_if_stmt : IF LPAREN expr RPAREN SEMI statement_list END SEMI'''
        if_node = ASTNode('if')
        # expr should be one child
        # statement_list should be another
        self.asts.append(if_node)

    def p_if_stmt_elseif(self, p):
        '''if_stmt_elseif : simple_if_stmt
                          | if_stmt_elseif ELSEIF LPAREN expr RPAREN statement_list END SEMI'''
        pass

    def p_if_stmt(self, p):
        '''if_stmt : if_stmt_elseif SEMI
                   | if_stmt_elseif ELSE statement_list END SEMI
                   | IF expr THEN statement SEMI'''
        pass

    def p_statement_list(self, p):
        '''statement_list : statement_list SEMI statement SEMI
                          | statement SEMI'''
        pass

    # probably a better idea to insert missing semis
    # def p_optional_semi(self, p):
        # '''optional_semi : SEMI
                         # | empty'''
        # pass

    # convenience rule to explicitly state production to nothing
    def p_empty(self, p):
        '''empty :'''
        pass


    def p_macro_declaration_statement(self, p):
        '''macro_declaration_statement : MACRO ID LPAREN param_list RPAREN SEMI statement_list END SEMI
                                       | MACRO ID statement_list END SEMI'''
        pass

    def p_param_list(self, p):
        '''param_list : param_decl
                      | param_decl COMMA param_list
                      | '''
        pass

    def p_param_decl(self, p):
        '''param_decl : ID
                      | assignment'''
        pass

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expr SEMI
                      | ID ASSIGNOP expr SEMI
                      | DEFAULT ASSIGN expr SEMI'''
        self.symbol_table[p[1]] = p[3]

    def p_expr_op(self, p):
        '''expr : expr OP expr'''
        print("Found unhandled operator: {}".format(p[2].value))

    def p_expr_plus(self, p):
        '''expr : expr PLUS term'''
        plus_node = ASTNode('+')
        plus_node.add_children([p[1], p[3]])
        self.asts.append(plus_node)
        p[0] = p[1] + p[3]

    def p_expr_id(self, p):
        '''expr : ID'''
        p[0] = self.symbol_table[p[1]]
        id_node = ASTNode('symbol')
        id_node.attributes['name'] = p[1]
        id_node.attributes['value'] = self.symbol_table.get(p[1], '*not found*')
        self.asts.append(id_node)

    def p_expr_minus(self, p):
        '''expr : expr MINUS term'''
        p[0] = p[1] - p[3]

    def p_expr_term(self, p):
        '''expr : term'''
        p[0] = p[1]

    def p_expr_null(self, p):
        '''expr : NULL'''
        p[0] = None

    def p_expr_true(self, p):
        '''expr : TRUE'''
        p[0] = True

    def p_expr_false(self, p):
        '''expr : FALSE'''
        p[0] = False

    def p_expr_range(self, p):
        '''expr : expr RANGE expr'''
        pass

    def p_expr_filter(self, p):
        '''expr : expr FILTER method_call'''
        pass

    def p_method_call(self, p):
        '''method_call : ID
                       | ID RPAREN param_list LPAREN'''
        pass

    def p_term_times(self, p):
        '''term : term TIMES factor'''
        p[0] = p[1] * p[3]


    def p_term_div(self, p):
        'term : term DIV factor'
        p[0] = p[1] / p[3]


    def p_term_mod(self, p):
        '''term : term MODULUS factor'''
        pass

    def p_term_factor(self, p):
        'term : factor'
        p[0] = p[1]


    def p_factor_num(self, p):
        'factor : NUMBER'
        p[0] = p[1]

    def p_factor_expr(self, p):
        'factor : LPAREN expr RPAREN'
        p[0] = p[2]

    def p_factor_id(self, p):
        '''factor : ID'''
        p[0] = self.symbol_table[p[1]]

    def p_include(self, p):
        '''include_stmt : INCLUDE STRING'''
        p[0] = p[2]

    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        badline = p.lexer.lexdata.split('\n')[p.lineno-1]
        print("Syntax error in input line {} at '{}'!".format(p.lineno, p.value))
        print(badline)
