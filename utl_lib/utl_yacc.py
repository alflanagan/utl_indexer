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
        :py:func:`ply.yacc.yacc` call. This turns on messages about the tables generated, and
        yacc warnings.

    """

    def __init__(self, handlers=None, debug=False):
        self.parsed = False
        # Some tokens get processed out before parsing
        # START_UTL is implicit when we get UTL token
        # but we need END_UTL since it can close a statment
        self.filtered_tokens = set(['COMMENT', 'START_UTL'])
        self.tokens = tuple(set(UTLLexer.tokens) - self.filtered_tokens)
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
        return self.parser.parse(input=input_text, lexer=self.utl_lexer, debug=debug,
                                 tokenfunc=self._filtered_token, tracking=tracking)

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
                     | DEFAULT expr eostmt
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

    def p_expr(self, p):
        '''expr : NOT expr
                | EXCLAMATION expr
                | NUMBER rexpr
                | MINUS expr %prec UMINUS
                | PLUS expr %prec UMINUS
                | STRING rexpr
                | FALSE rexpr
                | TRUE rexpr
                | NULL rexpr
                | ID rexpr
                | LPAREN expr RPAREN rexpr
                | array_literal RBRACKET rexpr'''
        pass

    # this is the set of productions which result from elimination of left-recursion in expr.
    # LPAREN, LBRACKET, PLUS, MINUS appear in both expr and rexpr because they can occur alone
    # or immediately following an expr -- each results in shift/reduce conflict, but yacc picks
    # correct option
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
                 | DOT expr
                 | ASSIGN expr
                 | ASSIGNOP expr
                 | LPAREN arg_list RPAREN rexpr
                 | LBRACKET expr RBRACKET rexpr'''
        pass

    def p_arg_list(self, p):
        '''arg_list :
                    | arg
                    | arg COMMA arg_list'''
        pass

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr
               | ID COLON expr'''
        pass

    def p_array_literal(self, p):
        '''array_literal : LBRACKET array_elems
                         | LBRACKET key_value_elems
                         | LBRACKET'''
        pass

    # third case below allows trailing comma in array literal
    # even with that, the UTL parser on Townnews allows situations not recognized, like [,].
    # Hopefully this covers most situations.
    def p_array_elems(self, p):
        '''array_elems : expr
                       | expr COMMA array_elems
                       | expr COMMA'''
        pass

    # third case below allows trailing comma in array literal
    def p_key_value_elems(self, p):
        '''key_value_elems : expr COLON expr
                           | expr COLON expr COMMA key_value_elems
                           | expr COLON expr COMMA'''
        pass

    def p_if_stmt(self, p):
        '''if_stmt : IF expr statement_list elseif_stmts else_stmt END'''
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
        '''return_stmt : RETURN expr
                       | RETURN'''
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
        '''include_stmt : INCLUDE expr'''
        pass

    def p_abbrev_if_stmt(self, p):
        '''abbrev_if_stmt : IF expr THEN statement'''
        pass

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expr statement_list END'''
        pass

    def p_call_stmt(self, p):
        '''call_stmt : CALL expr'''
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
