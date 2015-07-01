#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc

from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_parse_handler import UTLParseHandler


class UTLParser(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """Represents the current state of parsing a UTL code source, and generated AST.

    :param UTLParseHandler handlers: a (possibly empty) list of
        :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` instances containing methods to
        be invoked by various parse productions.

    :param Boolean debug: passed-through to the `debug` parameter in the
        :py:func:`ply.yacc.yacc` call.

    """

    def __init__(self, handlers=None, debug=True):
        self.parsed = False
        #self.tokens = UTLLexer.tokens[:]  # make copy, so we can .remove() tokens
        # Some tokens get processed out before parsing
        # START_UTL is implicit when we get UTL token
        # but we need END_UTL since it may close a statment
        #self.filtered_tokens = ['COMMENT', 'START_UTL']
        #for tok in self.filtered_tokens:
        #    self.tokens.remove(tok)
        self.tokens = ['PLUS','MINUS','FILTER','TIMES','DIV','MODULUS','DOT','DOUBLEBAR',
                       'RANGE','NEQ','LTE','OR','LT','EQ','IS','GT','AND','GTE','DOUBLEAMP',
                       'LPAREN','RPAREN','NOT','EXCLAMATION','NUMBER', 'START_UTL', 'DOCUMENT',
                       'STRING','ID','FALSE','TRUE','NULL', 'SEMI', 'END_UTL', 'COMMA', 'COLON',
                       'LBRACKET', 'RBRACKET', 'ASSIGN', 'ASSIGNOP', 'ECHO']

        self.parser = yacc.yacc(module=self, debug=debug)
        self.utl_lexer = UTLLexer()
        self.lexer = self.utl_lexer.lexer
        self.print_tokens = False  # may be set by parse()
        self.handlers = handlers
        """List of UTLParseHandler objects. Only the first one to return something besides
        :py:attr:`None` determines the return value from a production."""
        # silently accept single handler, don't except non-handlers
        if isinstance(self.handlers, UTLParseHandler):
            self.handlers = [self.handlers]
        else:
            for handler in self.handlers:
                if not isinstance(handler, UTLParseHandler):
                    raise ValueError('Got invalid handler object "{}", must be UTLParseHandler'
                                     ''.format(handler))


    # operator precedence based on PHP
    # https://secure.php.net/manual/en/language.operators.precedence.php
    # note lowest precedence is first (!)
    precedence = (
        ('left', 'OR'),
        ('left', 'DOUBLEBAR'),
        ('left', 'AND'),
        ('left', 'DOUBLEAMP'),
        ('left', 'ASSIGN', 'ASSIGNOP'),
        ('left', 'FILTER'),
        ('nonassoc', 'IS', 'NOT', 'EQ', 'NEQ'),
        ('nonassoc', 'LT', 'GT', 'LTE', 'GTE'),  # relational operators <, >, <=, >=
        ('left', 'PLUS', 'MINUS', 'DOT'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
        ('right', 'UMINUS'),  # same precedence as *, since  -5 == -1 * 5
        ('right', 'EXCLAMATION'),
        ('nonassoc', 'RANGE', 'COLON'),
        ('left', 'COMMA', 'LBRACKET', 'LPAREN', 'RBRACKET', 'RPAREN'),
    )

    # def _filtered_token(self):
        # """Like :py:meth:`token()` but does not pass on tokens in `self.filtered_tokens`."""
        # tok = self.utl_lexer.token()
        # while tok and tok.type in self.filtered_tokens:
            # tok = self.utl_lexer.token()
        # if tok and self.print_tokens:
            # print(tok)
        # return tok

    def parse(self, input_text=None, debug=False, tracking=False, print_tokens=False):
        """Parses the code in `input_text`, returns result.

        """
        self.print_tokens = print_tokens
        return self.parser.parse(input=input_text, lexer=self.utl_lexer, debug=debug)

    def p_utldoc(self, p):
        '''utldoc : START_UTL statement_list'''
        pass

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | statement'''
        pass

    def p_statement(self, p):
        '''statement : expr end_stmt
                     | echo_stmt end_stmt
                     | end_stmt
                     | DOCUMENT'''
        # | assignment end_stmt
        # | if_stmt end_stmt
        # | abbrev_if_stmt
        # | return_stmt end_stmt
        # | macro_defn end_stmt
        # | echo_stmt end_stmt
        # | for_stmt end_stmt
        # | include_stmt end_stmt
        # | while_stmt end_stmt
        # | call_stmt end_stmt
        # | BREAK end_stmt
        # | CONTINUE end_stmt
        # | EXIT end_stmt
        # | DOCUMENT
        # | end_stmt
        pass

    def p_end_stmt(self, p):
        '''end_stmt : SEMI
                    | END_UTL'''
        pass

    def p_echo_stmt(self, p):
        '''echo_stmt : ECHO
                     | ECHO expr'''
        pass

    def p_expr(self, p):
        '''expr : expr PLUS expr
                | expr MINUS expr
                | expr FILTER expr
                | expr TIMES expr
                | expr DIV expr
                | expr MODULUS expr
                | expr DOT expr
                | expr DOUBLEBAR expr
                | expr RANGE expr
                | expr NEQ expr
                | expr LTE expr
                | expr OR expr
                | expr LT expr
                | expr EQ expr
                | expr IS expr
                | expr GT expr
                | expr AND expr
                | expr GTE expr
                | expr DOUBLEAMP expr
                | assignment
                | LPAREN expr RPAREN
                | NOT expr
                | EXCLAMATION expr
                | NUMBER
                | MINUS NUMBER %prec UMINUS
                | PLUS NUMBER %prec UMINUS
                | STRING
                | array_literal
                | ID
                | array_ref
                | FALSE
                | TRUE
                | NULL
                | method_call'''
        pass

    # def p_param_list(self, p):
        # '''param_list :
                      # | param_list COMMA param_decl
                      # | param_decl '''
        # for handler in self.handlers:
            # value = None  # default for empty list
            # if len(p) == 2:
                # value = handler.param_list(p[1], None)
            # elif len(p) == 4:
                # value = handler.param_list(p[3], p[1])
            # if p[0] is None:
                # p[0] = value

    # def p_param_decl(self, p):
        # '''param_decl : ID
                      # | ID ASSIGN expr'''
        # for handler in self.handlers:
            # if len(p) == 2:
                # value = handler.param_decl(p[1], None)
            # else:
                # value = handler.param_decl(p[1], p[3])
            # if p[0] is None:
                # p[0] = value

    def p_arg_list(self, p):
        '''arg_list :
                    | arg
                    | arg_list COMMA arg'''
        pass

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr'''
        pass

    def p_assignment(self, p):
        '''assignment : expr ASSIGN expr
                      | expr ASSIGNOP expr'''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.assignment(p[1], p[3], p[2], False)
            else:
                value = handler.assignment(p[2], p[4], p[3], True)
            if p[0] is None:
                p[0] = value

    def p_method_call(self, p):
        '''method_call : expr LPAREN arg_list RPAREN'''
        for handler in self.handlers:
            value = handler.method_call(p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_array_literal(self, p):
        '''array_literal : LBRACKET array_elems RBRACKET
                         | LBRACKET key_value_elems RBRACKET
                         | LBRACKET RBRACKET'''
        for handler in self.handlers:
            value = handler.array_literal(p[2] if len(p)==4 else None)
            if p[0] is None:
                p[0] = value

    def p_array_elems(self, p):
        '''array_elems : expr
                       | array_elems COMMA expr'''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.array_elems(p[3], p[1])
            else:
                value = handler.array_elems(p[1], None)
            if p[0] is None:
                p[0] = value

    def p_key_value_elems(self, p):
        '''key_value_elems : expr COLON expr
                           | key_value_elems COMMA expr COLON expr'''
        for handler in self.handlers:
            if len(p) == 6:
                value = handler.key_value_elems(p[3], p[5], p[1])
            else:
                value = handler.key_value_elems(p[1], p[3], None)
            if p[0] is None:
                p[0] = value

    def p_array_ref(self, p):
        '''array_ref : expr LBRACKET expr RBRACKET'''
        for handler in self.handlers:
            value = handler.array_ref(p[1], p[3])
            if p[0] is None:
                p[0] = value

    # def p_if_stmt(self, p):
        # '''if_stmt : IF expr statement_list elseif_stmts else_stmt END'''
        # for handler in self.handlers:
            # value = handler.if_stmt(p[2], p[3], p[4], p[5])
            # if p[0] is None:
                # p[0] = value

    # def p_elseif_stmts(self, p):
        # '''elseif_stmts : elseif_stmts elseif_stmt
                        # |'''
        # for handler in self.handlers:
            # if len(p) == 3:
                # value = handler.elseif_stmts(p[2], p[1])
                # if p[0] is None:
                    # p[0] = value

    # def p_elseif_stmt(self, p):
        # '''elseif_stmt : ELSEIF expr statement_list'''
        # for handler in self.handlers:
            # value = handler.elseif_stmt(p[2], p[3])
            # if p[0] is None:
                # p[0] = value

    # def p_else_stmt(self, p):
        # '''else_stmt : ELSE statement_list
                     # |'''
        # for handler in self.handlers:
            # if len(p) == 3:
                # value = handler.else_stmt(p[2])
                # if p[0] is None:
                    # p[0] = value

    # def p_return_stmt(self, p):
        # '''return_stmt : RETURN expr'''
        # for handler in self.handlers:
            # value = handler.return_stmt(p[2])
            # if p[0] is None:
                # p[0] = value

    # def p_macro_defn(self, p):
        # '''macro_defn : macro_decl end_stmt statement_list END
                      # | macro_decl end_stmt END'''
        # for handler in self.handlers:
            # if len(p) == 4:
                # value = handler.macro_defn(p[1], None)
            # else:
                # value = handler.macro_defn(p[1], p[3])
            # if p[0] is None:
                # p[0] = value

    # def p_macro_decl(self, p):
        # '''macro_decl : MACRO dotted_id
                      # | MACRO dotted_id LPAREN param_list RPAREN
        # '''
        # for handler in self.handlers:
            # value = handler.macro_decl(p[2], None if len(p) < 5 else p[4])
            # if p[0] is None:
                # p[0] = value

    # def p_dotted_id(self, p):
        # '''dotted_id : ID
                     # | dotted_id DOT ID'''
        # pass

    # def p_for_stmt(self, p):
        # '''for_stmt : FOR expr as_clause end_stmt statement_list END
                    # | FOR EACH expr as_clause end_stmt statement_list END'''
        # for handler in self.handlers:
            # if self._ssa(p, 2) == 'each':
                # value = handler.for_stmt(p[3], p[4], p[6])
            # else:
                # value = handler.for_stmt(p[2], p[3], p[5])
            # if p[0] is None:
                # p[0] = value

    # def p_as_clause(self, p):
        # '''as_clause :
                     # | AS ID
                     # | AS ID COMMA ID'''
        # for handler in self.handlers:
            # value = handler.as_clause(p[2] if len(p) > 2 else None,
                                      # p[4] if len(p) > 4 else None)
            # if p[0] is None:
                # p[0] = value

    # def p_include_stmt(self, p):
        # '''include_stmt : INCLUDE STRING'''
        # for handler in self.handlers:
            # value = handler.include_stmt(p[2])
            # if p[0] is None:
                # p[0] = value

    # def p_abbrev_if_stmt(self, p):
        # '''abbrev_if_stmt : IF expr THEN statement'''
        # for handler in self.handlers:
            # value = handler.abbrev_if_stmt(p[2], p[4])
            # if p[0] is None:
                # p[0] = value

    # def p_while_stmt(self, p):
        # '''while_stmt : WHILE expr statement_list END'''
        # for handler in self.handlers:
            # value = handler.while_stmt(p[2], p[3])
            # if p[0] is None:
                # p[0] = value

    # def p_call_stmt(self, p):
        # '''call_stmt : CALL method_call'''
        # for handler in self.handlers:
            # value = handler.call_stmt(p[2])
            # if p[0] is None:
                # p[0] = value

    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        for handler in self.handlers:
            handler.error(p, self.parser)
