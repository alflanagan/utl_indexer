#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""
import sys
import ply.yacc as yacc

from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_parse_handler import UTLParseHandler


class UTLParser(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """Represents the current state of parsing a UTL code source.

    :param UTLParseHandler handlers: a (possibly empty) list of
        :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` instances containing methods to
        be invoked by various parse productions.

    :param Boolean debug: passed-through to the `debug` parameter in the
        :py:func:`ply.yacc.yacc` call.

    """

    def __init__(self, handlers=None, debug=True):
        self.parsed = False
        # self.tokens = UTLLexer.tokens[:]  # make copy, so we can .remove() tokens
        # Some tokens get processed out before parsing
        # START_UTL is implicit when we get UTL token
        # but we need END_UTL since it may close a statment
        # self.filtered_tokens = ['COMMENT', 'START_UTL']
        # for tok in self.filtered_tokens:
        #     self.tokens.remove(tok)
        self.tokens = ['AND', 'AS', 'ASSIGN', 'ASSIGNOP', 'BREAK', 'CALL', 'COLON', 'COMMA',
                       'CONTINUE', 'DEFAULT', 'DIV', 'DOCUMENT', 'DOT', 'DOUBLEAMP', 'DOUBLEBAR', 'EACH',
                       'ECHO', 'ELSE', 'ELSEIF', 'END', 'END_UTL', 'EOF', 'EQ', 'EXCLAMATION', 'EXIT', 'FALSE',
                       'FILTER', 'FOR', 'GT', 'GTE', 'ID', 'IF', 'INCLUDE', 'IS', 'LBRACKET', 'LPAREN', 'LT',
                       'LTE', 'MACRO', 'MINUS', 'MODULUS', 'NEQ', 'NOT', 'NULL', 'NUMBER', 'OR', 'PLUS', 'RANGE',
                       'RBRACKET', 'RETURN', 'RPAREN', 'SEMI', 'STRING', 'THEN', 'TIMES', 'TRUE', 'WHILE', ]

        self.parser = yacc.yacc(module=self, debug=debug)
        self.utl_lexer = UTLLexer()
        self.lexer = self.utl_lexer.lexer
        self.print_tokens = False  # may be set by parse()
        self.handlers = handlers
        self.error_count = 0
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
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
        ('right', 'UMINUS'),  # same precedence as *, since  -5 == -1 * 5
        ('right', 'EXCLAMATION'),
        ('nonassoc', 'RANGE', 'COLON'),
        ('left', 'COMMA'),
        ('right', 'LPAREN', 'LBRACKET'),
        ('left', 'DOT'),
    )

    def _filtered_token(self):
        """Like :py:meth:`token()` but does not pass on tokens not in `self.tokens`."""
        tok = self.utl_lexer.token()
        while tok and tok.type not in self.tokens:
            tok = self.utl_lexer.token()
        # if tok and self.print_tokens:
            # print(tok)
        return tok

    def parse(self, input_text=None, debug=False, tracking=False, print_tokens=False):
        """Parses the code in `input_text`, returns result.

        """
        self.print_tokens = print_tokens
        return self.parser.parse(input=input_text, lexer=self.utl_lexer,
                                 debug=debug, tokenfunc=self._filtered_token)

    def p_utldoc(self, p):
        '''utldoc : statement_list'''
        pass

    def p_statement_list(self, p):
        ''' statement_list : statement
                           | statement statement_list'''
        pass

    def p_eostmt(self, p):
        '''eostmt : SEMI
                  | EOF
                  | END_UTL'''
        pass

    def p_statement(self, p):
        '''statement : eostmt
                     | echo_stmt eostmt
                     | for_stmt eostmt
                     | abbrev_if_stmt
                     | if_stmt eostmt
                     | DOCUMENT
                     | expr eostmt
                     | assignment eostmt
                     | return_stmt eostmt
                     | include_stmt eostmt
                     | call_stmt eostmt
                     | macro_defn eostmt
                     | while_stmt eostmt
                     | BREAK eostmt
                     | CONTINUE eostmt
                     | EXIT eostmt'''
        pass

    def p_echo_stmt(self, p):
        '''echo_stmt : ECHO
                     | ECHO expr'''
        pass

    def p_assignment(self, p):
        '''assignment : expr ASSIGN expr
                      | DEFAULT expr ASSIGN expr
                      | expr ASSIGNOP expr'''
        pass

    def p_expr(self, p):
        '''expr : array_literal rexpr
                | LPAREN expr RPAREN rexpr
                | NOT expr rexpr
                | EXCLAMATION expr rexpr
                | NUMBER rexpr
                | MINUS expr rexpr %prec UMINUS
                | PLUS expr rexpr %prec UMINUS
                | STRING rexpr
                | FALSE rexpr
                | TRUE rexpr
                | NULL rexpr
                | ID rexpr
                | method_call rexpr'''
        pass

    # this is the set of productions which, if put back into p_expr, would cause a
    # left-recursive production
    # each production (except empty) generates a shift/reduce conflict with each production in
    # expr that includes rexpr
    # so we have 13 (expr) * 20 (rexpr) === 260 shift/reduce conflicts
    # but it works, dammit!
    def p_rexpr(self, p):
        '''rexpr :
                 | PLUS expr
                 | MINUS expr
                 | FILTER expr
                 | TIMES expr
                 | DIV expr
                 | MODULUS expr
                 | DOUBLEBAR expr
                 | RANGE expr
                 | NEQ expr
                 | LTE expr
                 | OR expr
                 | LT expr
                 | EQ expr
                 | IS expr
                 | GT expr
                 | AND expr
                 | GTE expr
                 | DOUBLEAMP expr
                 | LBRACKET expr RBRACKET
                 | DOT expr'''
        pass

    def p_arg_list(self, p):
        '''arg_list : arg
                    | arg COMMA arg_list'''
        pass

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr'''
        pass


    def p_method_call(self, p):
        '''method_call : expr LPAREN arg_list RPAREN
                       | expr LPAREN RPAREN'''
        pass

    def p_array_literal(self, p):
        '''array_literal : LBRACKET array_elems RBRACKET
                         | LBRACKET key_value_elems RBRACKET
                         | LBRACKET RBRACKET'''
        pass

    def p_array_elems(self, p):
        '''array_elems : expr
                       | expr COMMA array_elems'''
        pass

    def p_key_value_elems(self, p):
        '''key_value_elems : expr COLON expr
                           | expr COLON expr COMMA key_value_elems'''
        pass

    def p_if_stmt(self, p):
        '''if_stmt : IF statement_list elseif_stmts else_stmt END'''
        pass

    def p_elseif_stmts(self, p):
        '''elseif_stmts :
                        | elseif_stmt elseif_stmts'''
        pass

    def p_elseif_stmt(self, p):
        '''elseif_stmt : ELSEIF expr statement_list'''
        pass

    def p_else_stmt(self, p):
        '''else_stmt :
                     | ELSE statement_list'''
        pass

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expr'''
        pass


    def p_param_list(self, p):
        '''param_list :
                      | param_decl COMMA param_list
                      | param_decl '''
        pass

    def p_param_decl(self, p):
        '''param_decl : ID
                      | ID ASSIGN expr'''
        pass

    def p_macro_defn(self, p):
        '''macro_defn : macro_decl eostmt statement_list END
                      | macro_decl eostmt END'''
        pass

    def p_macro_decl(self, p):
        '''macro_decl : MACRO dotted_id
                      | MACRO dotted_id LPAREN param_list RPAREN
        '''
        pass

    def p_dotted_id(self, p):
        '''dotted_id : ID
                     | ID DOT dotted_id'''
        pass

    def p_for_stmt(self, p):
        '''for_stmt : FOR expr as_clause eostmt statement_list END
                    | FOR EACH expr as_clause eostmt statement_list END'''
        pass

    def p_as_clause(self, p):
        '''as_clause :
                     | AS ID
                     | AS ID COMMA ID'''
        pass

    def p_include_stmt(self, p):
        '''include_stmt : INCLUDE STRING'''
        pass

    def p_abbrev_if_stmt(self, p):
        '''abbrev_if_stmt : IF expr THEN statement'''
        pass

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expr statement_list END'''
        pass

    def p_call_stmt(self, p):
        '''call_stmt : CALL method_call'''
        pass

    # Error rule for syntax errors
    def p_error(self, p):  # pylint: disable=missing-docstring
        # IF top_symbol IS 'expr'
        # AND next IS SEMI or END_UTL
        #    pop top symbol value
        #    push ECHO
        #    push top symbol
        #    try again
        # END
        self.error_count += 1
        if not self.handlers:
            sys.stderr.write("Error in statement, line {}! {}\n".format(p.lexer.lineno(), p))
        # is there an expr on the stack?
        # if so, remove it, push "ECHO", push expr.
        for handler in self.handlers:
            handler.error(p, self.parser)
