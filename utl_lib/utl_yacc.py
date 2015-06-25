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
        self.tokens = UTLLexer.tokens[:]  # make copy, so we can .remove() tokens
        # Some tokens get processed out before parsing
        # can't handle DOCUMENT as regular statement because it can occur anywhere
        # START_UTL is implicit when we get UTL token
        # but we need END_UTL since it may close a statment
        self.filtered_tokens = ['COMMENT', 'START_UTL']
        for tok in self.filtered_tokens:
            self.tokens.remove(tok)
        self.parser = yacc.yacc(module=self, debug=debug)
        self.utl_lexer = UTLLexer()
        self.lexer = self.utl_lexer.lexer
        self.print_tokens = False  # may be set by parse()
        self.handlers = handlers
        """List of UTLParseHandler objects. Only the first one to return something besides
        :py:attr:`None` determines the return value from a production."""
        if isinstance(self.handlers, UTLParseHandler):
            self.handlers = [self.handlers]
        else:
            for handler in self.handlers:
                if not isinstance(handler, UTLParseHandler):
                    raise ValueError('Got invalid handler object "{}", must be UTLParseHandler'
                                     ''.format(handler))

    precedence = (
        ('right', 'NOT'),
        ('left', 'PLUS', 'MINUS', 'OP'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
    )

    def _filtered_token(self):
        """Like :py:meth:`token()` but does not pass on tokens in `self.filtered_tokens`."""
        tok = self.utl_lexer.token()
        while tok and tok.type in self.filtered_tokens:
            tok = self.utl_lexer.token()
        if tok and self.print_tokens:
            print(tok)
        return tok

    def parse(self, input_text=None, debug=False, tracking=False, print_tokens=False):
        """Parses the code in `input_text`, returns result.

        """
        self.print_tokens = print_tokens
        return self.parser.parse(input=input_text, lexer=self.utl_lexer, debug=debug,
                                 tracking=tracking, tokenfunc=self._filtered_token)

    def p_utldoc(self, p):
        '''utldoc : statement_list'''
        for handler in self.handlers:
            value = handler.utldoc(p[1])
            if p[0] is None:
                p[0] = value

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | statement'''
        for handler in self.handlers:
            if len(p) == 2:
                value = handler.statement_list(p[1])
            else:
                value = handler.statement_list(p[2], p[1])
            if p[0] is None:
                p[0] = value

    def p_statement(self, p):
        '''statement : expr end_stmt
                     | assignment end_stmt
                     | if_stmt end_stmt
                     | abbrev_if_stmt end_stmt
                     | return_stmt end_stmt
                     | macro_defn end_stmt
                     | echo_stmt end_stmt
                     | for_stmt end_stmt
                     | include_stmt end_stmt
                     | while_stmt end_stmt
                     | call_stmt end_stmt
                     | BREAK end_stmt
                     | CONTINUE end_stmt
                     | EXIT end_stmt
                     | DOCUMENT
                     | end_stmt'''
        for handler in self.handlers:
            if p[1]:  # excludes end_stmt
                value = handler.statement(p[1], len(p) == 2)  # test is True only for DOCUMENT
                if p[0] is None:
                    p[0] = value

    def p_end_stmt(self, p):
        '''end_stmt : SEMI
                    | END_UTL'''
        for handler in self.handlers:
            value = handler.end_stmt(p[1])
            if p[0] is None:
                p[0] = value

    def p_echo_stmt(self, p):
        '''echo_stmt : ECHO
                     | ECHO expr'''
        for handler in self.handlers:
            if len(p) > 2:
                value = handler.echo_stmt(p[2])
                if p[0] is None:
                    p[0] = value

    def p_expr(self, p):
        '''expr : expr PLUS term
                | expr MINUS term
                | term
                | expr FILTER method_call
                | expr FILTER full_id
                | expr OP expr
                | NOT expr
                '''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.expr(p[1], p[3], p[2])
            elif len(p) == 3:  # NOT expr
                value = handler.expr(p[2], None, p[1])
            else:  # term
                value = handler.expr(None, p[1], None)
            if p[0] is None:
                p[0] = value

    def p_param_list(self, p):
        '''param_list :
                      | param_list COMMA param_decl
                      | param_decl '''
        for handler in self.handlers:
            value = None  # default for empty list
            if len(p) == 2:
                value = handler.param_list(p[1], None)
            elif len(p) == 4:
                value = handler.param_list(p[3], p[1])
            if p[0] is None:
                p[0] = value

    def p_param_decl(self, p):
        '''param_decl : ID
                      | assignment'''
        for handler in self.handlers:
            if isinstance(p[1], str):  # ID
                value = handler.param_decl(p[1], None)
            else:
                value = handler.param_decl(None, p[1])
            if p[0] is None:
                p[0] = value

    def p_arg_list(self, p):
        '''arg_list :
                    | arg
                    | arg_list COMMA arg'''
        for handler in self.handlers:
            if len(p) == 1:
                value = handler.arg_list(None, None)
            elif len(p) == 2:
                value = handler.arg_list(p[1], None)
            else:
                value = handler.arg_list(p[3], p[1])
            if p[0] is None:
                p[0] = value

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr'''
        for handler in self.handlers:
            value = handler.arg(p[1], p[3] if len(p) == 4 else None)
            if p[0] is None:
                p[0] = value

    def p_assignment(self, p):
        '''assignment : full_id ASSIGN expr
                      | full_id ASSIGNOP expr
                      | DEFAULT full_id ASSIGN expr
                      | DEFAULT full_id ASSIGNOP expr'''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.assignment(p[1], p[3], p[2], False)
            else:
                value = handler.assignment(p[2], p[4], p[3], True)
            if p[0] is None:
                p[0] = value

    def p_method_call(self, p):
        '''method_call : full_id LPAREN arg_list RPAREN'''
        for handler in self.handlers:
            value = handler.method_call(p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_full_id(self, p):
        '''full_id : ID
                   | full_id DOT ID'''
        for handler in self.handlers:
            value = handler.full_id(p[1], None if len(p) == 2 else p[3])
            if p[0] is None:
                p[0] = value

    def p_term(self, p):
        '''term : term TIMES factor
                | term DIV factor
                | term MODULUS factor
                | factor'''
        for handler in self.handlers:
            if len(p) == 2:
                value = handler.term(p[1], None, None)
            else:
                value = handler.term(p[1], p[2], p[3])
            if p[0] is None:
                p[0] = value

    def p_factor(self, p):
        '''factor : literal
                  | full_id
                  | array_ref
                  | FALSE
                  | TRUE
                  | NULL
                  | LPAREN expr RPAREN
                  | method_call'''
        for handler in self.handlers:
            # odd we allow string here, but "5" can auto-convert to 5.0, so it's legal
            if len(p) == 2:
                if isinstance(p[1], str):  # keyword
                    value = handler.factor(None, p[1], None)
                else:  # production
                    value = handler.factor(p[1], None, None)
            else:  # parenthesized expr
                value = handler.factor(None, None, p[2])
            if p[0] is None:
                p[0] = value

    def p_literal(self, p):
        '''literal : NUMBER
                   | STRING'''
        for handler in self.handlers:
            value = handler.literal(p[1])
            if p[0] is None:
                p[0] = value

    def p_array_ref(self, p):
        '''array_ref : full_id LBRACKET expr RBRACKET'''
        for handler in self.handlers:
            value = handler.array_ref(p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_if_stmt(self, p):
        '''if_stmt : IF expr statement_list elseif_stmts else_stmt END'''
        for handler in self.handlers:
            value = handler.if_stmt(p[2], p[3], p[4], p[5])
            if p[0] is None:
                p[0] = value

    def p_elseif_stmts(self, p):
        '''elseif_stmts : elseif_stmts elseif_stmt
                        |'''
        for handler in self.handlers:
            if len(p) == 3:
                value = handler.elseif_stmts(p[2], p[1])
                if p[0] is None:
                    p[0] = value

    def p_elseif_stmt(self, p):
        '''elseif_stmt : ELSEIF expr statement_list'''
        for handler in self.handlers:
            value = handler.elseif_stmt(p[2], p[3])
            if p[0] is None:
                p[0] = value

    def p_else_stmt(self, p):
        '''else_stmt : ELSE statement_list
                     |'''
        for handler in self.handlers:
            if len(p) == 3:
                value = handler.else_stmt(p[2])
                if p[0] is None:
                    p[0] = value

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expr'''
        for handler in self.handlers:
            value = handler.return_stmt(p[2])
            if p[0] is None:
                p[0] = value

    def p_macro_defn(self, p):
        '''macro_defn : macro_decl end_stmt statement_list END
                      | macro_decl end_stmt END'''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.macro_defn(p[1], None)
            else:
                assert len(p) == 5
                value = handler.macro_defn(p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_macro_decl(self, p):
        '''macro_decl : MACRO full_id
                      | MACRO full_id LPAREN param_list RPAREN
        '''
        for handler in self.handlers:
            value = handler.macro_decl(p[2], None if len(p) < 5 else p[4])
            if p[0] is None:
                p[0] = value

    @staticmethod
    def _ssa(arr, ndx):
        """Safe string at: if ``arr[ndx]`` is a :py:class:`str`, return its :py:meth:`str.lower`.
        Otherwise, return an empty string.

        """
        try:
            return arr[ndx].lower()
        except (IndexError, AttributeError):
            return ""

    def p_for_stmt(self, p):
        '''for_stmt : FOR expr AS ID end_stmt statement_list END
                    | FOR expr end_stmt statement_list END
                    | FOR EACH expr AS ID end_stmt statement_list END
                    | FOR EACH expr end_stmt statement_list END'''
        for handler in self.handlers:
            if self._ssa(p, 2) == 'each':
                if self._ssa(p, 4) == 'as':
                    value = handler.for_stmt(p[3], p[5], p[7])
                else:
                    value = handler.for_stmt(p[3], None, p[5])
            else:
                if self._ssa(p, 3) == 'as':
                    value = handler.for_stmt(p[2], p[4], p[6])
                else:
                    value = handler.for_stmt(p[2], None, p[4])
            if p[0] is None:
                p[0] = value

    def p_include_stmt(self, p):
        '''include_stmt : INCLUDE STRING'''
        for handler in self.handlers:
            value = handler.include_stmt(p[2])
            if p[0] is None:
                p[0] = value

    def p_abbrev_if_stmt(self, p):
        '''abbrev_if_stmt : IF expr THEN statement'''
        for handler in self.handlers:
            value = handler.abbrev_if_stmt(p[2], p[4])
            if p[0] is None:
                p[0] = value

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expr statement_list END'''
        for handler in self.handlers:
            value = handler.while_stmt(p[2], p[3])
            if p[0] is None:
                p[0] = value

    def p_call_stmt(self, p):
        '''call_stmt : CALL method_call'''
        for handler in self.handlers:
            value = handler.call_stmt(p[2])
            if p[0] is None:
                p[0] = value

    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        for handler in self.handlers:
            handler.error(p)
