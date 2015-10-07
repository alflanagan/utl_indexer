#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""
import sys
import ply.yacc as yacc

from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_parse_handler import UTLParseHandler
import collections


class FrozenDict(collections.Mapping):
    """Immutable dictionary class by Raymond Hettinger himself."""
    # TODO: add an .update() method that returns a new FrozenDict
    def __init__(self, somedict):
        self._dict = dict(somedict)   # make a copy
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._dict.items()))
        return self._hash

    def __eq__(self, other):
        return self._dict == other._dict

    def combine(self, *args, **keys):
        """D.combine([E, ]**F) -> D'.  Create FrozenSet D' from D and dict/iterable E and F.

    D' is initially a copy of D.
    If E is present and has a .keys() method, then does:  for k in E: D'[k] = E[k]
    If E is present and lacks a .keys() method, then does:  for k, v in E: D'[k] = v
    In either case, this is followed by: for k in F:  D'[k] = F[k]

    """
        # yes, above is a direct steal from dict.update() docstring.
        newdict = self._dict.copy()
        newdict.update(*args, **keys)
        return FrozenDict(newdict)

class UTLParser(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """Represents the current state of parsing a UTL code source.

    :param UTLParseHandler handlers: a (possibly empty) list of
        :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` instances containing methods to
        be invoked by various parse productions.

    :param Boolean debug: passed-through to the `debug` parameter in the
        :py:func:`ply.yacc.yacc` call. This turns on messages about the tables generated, and
        yacc warnings.

    """
    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
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
        self.filename = ''  # may be set by parse()
        self.error_count = 0
        self._handlers = []
        self.handlers = handlers
        self.start = 0  # character offset where the current production starts
        self.end = 0   # character offset where the current production ends
        self.line = 0   # line number where the current production begins

    # operator precedence based on PHP
    # https://secure.php.net/manual/en/language.operators.precedence.php
    # note lowest precedence is first (!)
    precedence = (
        ('left', 'OR'),
        ('left', 'DOUBLEBAR'),
        ('left', 'AND'),
        ('left', 'DOUBLEAMP'),
        ('nonassoc', 'ASSIGN', 'ASSIGNOP'),
        ('nonassoc', 'IS', 'NOT', 'EQ', 'NEQ'),
        ('nonassoc', 'LT', 'GT', 'LTE', 'GTE'),  # relational operators <, >, <=, >=
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
        ('right', 'EXCLAMATION'),
        ('nonassoc', 'RANGE', 'COLON'),
        ('left', 'FILTER'),
        ('left', 'COMMA'),
        ('right', 'UMINUS'),
        ('right', 'LPAREN', 'LBRACKET'),
        # fixes shift/reduce conflict between array reference and array literal
        ('left', 'RBRACKET'),
        ('right', 'DOT'),
    )

    def _filtered_token(self):
        """Like :py:meth:`token()` but does not pass on tokens not in `self.tokens`."""
        tok = self.utl_lexer.token()
        while tok and tok.type not in self.tokens:
            tok = self.utl_lexer.token()
        # if tok and self.print_tokens:
            # print(tok)
        return tok

    @staticmethod
    def _(p, index):
        """convenient shortcut for `p[index] if len(p) > index else None`."""
        try:
            return p[index]
        except IndexError:
            return None

    def parse(self, input_text=None, debug=False, tracking=True, print_tokens=False,
              filename=''):
        """Parses the code in `input_text`, returns result.

        """
        self.print_tokens = print_tokens
        self.filename = filename
        return self.parser.parse(input=input_text, lexer=self.utl_lexer, debug=debug,
                                 tokenfunc=self._filtered_token, tracking=tracking)

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
            handler.error(self, p)

    @property
    def symstack(self):
        """The stack of grammar symbols."""
        # great, the property gets called when yacc.yacc() is called
        if hasattr(self, 'parser'):
            return self.parser.symstack
        return None

    def restart(self, new_handlers=None):
        """Return the parser to the state it had before any actual parsing was done. This should
        be significantly faster than creating a new parser instance.

        :param list new_handlers: a list of
        :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` instances which will be used to
        process productions in subsequent parses. A value of :py:attr:`None`, or no value at
        all, will keep the previously set handler list. To clear the list of handlers, pass an
        empty list.

        """
        # parser stacks created on parse, if they don't exist nothing to restart
        if hasattr(self.parser, "statestack"):
            self.parser.restart()
        self.utl_lexer = UTLLexer()  # possible to reset?
        self.lexer = self.utl_lexer.lexer
        self.print_tokens = False  # may be set by parse()
        self.filename = ''  # may be set by parse()
        self.error_count = 0
        if new_handlers is not None:
            self.handlers = new_handlers

    @property
    def handlers(self):
        """List of :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` objects. They are
        called in list order for each production reduced during the parse. The first handler to
        return a value that is not :py:attr:`None` determines the value assigned to the
        production.

        :raises ValueError: if set to anything other than [], :py:attr:`None` (equiv. to []), or
        an iterable whose members are all instances of
        :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler`.

        """
        # weirdly gets called before __init__
        try:
            return self._handlers
        except AttributeError:
            return None

    @handlers.setter
    def handlers(self, new_handlers):
        """A list of :py:class:`~utl_lib.utl_parse_handler.UTLParseHandler` instances.

        The matching method of each handler is called whenever a production is reduced.

        """
        # silently accept single handler, don't accept non-handlers
        if new_handlers is None:
            self._handlers = []
        elif isinstance(new_handlers, UTLParseHandler):
            self._handlers = [new_handlers]
        else:
            self._handlers = []
            for handler in new_handlers:
                if not isinstance(handler, UTLParseHandler):
                    raise ValueError('Got invalid handler object "{}", must be UTLParseHandler'
                                     ''.format(handler))
                self._handlers.append(handler)

    @handlers.deleter
    def handlers(self):
        del self._handlers

    @property
    def context(self):
        """Constructs and returns a dictionary describing the current context.

        Convenience method for the common case where certain values are needed in an immutable
        package.

        """
        if hasattr(self, 'end'):  # guard against ply.yacc weirdness
            return FrozenDict({"end": self.end, "file": self.filename, "start": self.start,
                               "line": self.line})

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def p_utldoc(self, p):
        '''utldoc : statement_list'''
        for handler in self.handlers:
            value = handler.utldoc(self, p[1])
            if p[0] is None:
                p[0] = value

    def p_statement_list(self, p):
        ''' statement_list : statement
                           | statement statement_list'''
        if p[1] is not None or self._(p, 2) is not None:
            for handler in self.handlers:
                value = handler.statement_list(self, p[1], self._(p, 2))
                if p[0] is None:
                    p[0] = value

    def p_statement(self, p):
        '''statement : eostmt
                     | echo_stmt eostmt
                     | for_stmt eostmt
                     | abbrev_if_stmt
                     | if_stmt eostmt
                     | DOCUMENT
                     | expr eostmt
                     | default_assignment eostmt
                     | return_stmt eostmt
                     | include_stmt eostmt
                     | call_stmt eostmt
                     | macro_defn eostmt
                     | while_stmt eostmt
                     | BREAK eostmt
                     | CONTINUE eostmt
                     | EXIT eostmt'''
        if p[1] is not None:  # skip empty statements
            for handler in self.handlers:
                value = handler.statement(self, p[1])
                if p[0] is None:
                    p[0] = value

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def p_abbrev_if_stmt(self, p):
        '''abbrev_if_stmt : IF expr THEN statement'''
        for handler in self.handlers:
            value = handler.abbrev_if_stmt(self, p[2], p[4])
            if p[0] is None:
                p[0] = value

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr %prec RBRACKET
               | ID COLON expr %prec RBRACKET'''
        # shift/reduce between expr->STRING, expr->ID, and STRING COLON, ID COLON
        # is there a better way to handle shift/reduce than explicitly settting precedence?
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.arg(self, p[3], p[1])
            else:
                value = handler.arg(self, p[1], None)
            if p[0] is None:
                p[0] = value

    def p_arg_list(self, p):
        '''arg_list : arg
                    | arg COMMA arg_list'''
        for handler in self.handlers:
            value = handler.arg_list(self, p[1], self._(p, 3))
            if p[0] is None:
                p[0] = value

    def p_array_elems(self, p):
        '''array_elems : expr
                       | array_elems COMMA expr'''
        for handler in self.handlers:
            if len(p) == 2:
                value = handler.array_elems(self, p[1], None)
            else:
                value = handler.array_elems(self, p[3], p[1])
            if p[0] is None:
                p[0] = value

    def p_array_literal(self, p):
        '''array_literal : LBRACKET RBRACKET
                         | LBRACKET array_elems RBRACKET
                         | LBRACKET array_elems COMMA RBRACKET'''
        for handler in self.handlers:
            value = handler.array_literal(self, p[2] if len(p) >= 4 else None)
            if p[0] is None:
                p[0] = value

    def p_array_ref(self, p):
        '''array_ref : expr LBRACKET expr RBRACKET'''
        # of course, not all array literal expressions are valid for array reference
        for handler in self.handlers:
            value = handler.array_ref(self, p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_as_clause(self, p):
        '''as_clause :
                     | AS ID
                     | AS ID COMMA ID'''
        if len(p) > 1:
            for handler in self.handlers:
                value = handler.as_clause(self, p[2], self._(p, 4))
                if p[0] is None:
                    p[0] = value

    def p_call_stmt(self, p):
        '''call_stmt : CALL macro_call'''
        for handler in self.handlers:
            value = handler.call_stmt(self, p[2])
            if p[0] is None:
                p[0] = value

    def p_default_assignment(self, p):
        '''default_assignment : DEFAULT expr'''
        for handler in self.handlers:
            value = handler.default_assignment(self, p[2])
            if p[0] is None:
                p[0] = value

    def p_dotted_id(self, p):
        '''dotted_id : ID
                     | ID DOT dotted_id'''
        for handler in self.handlers:
            value = handler.dotted_id(self, p[1], self._(p, 3))
            if p[0] is None:
                p[0] = value

    def p_echo_stmt(self, p):
        '''echo_stmt : ECHO
                     | ECHO expr'''
        self.start = p.lexpos(1)
        if len(p) == 3:
            self.end = p[2].attributes["end"]
        else:
            self.end = start + 4
        self.line = 0
        for handler in self.handlers:
            value = handler.echo_stmt(self, self._(p, 2))
            if p[0] is None:
                p[0] = value

    def p_else_stmt(self, p):
        '''else_stmt :
                     | ELSE statement_list'''
        if len(p) > 1:
            for handler in self.handlers:
                value = handler.else_stmt(self, p[2])
                if p[0] is None:
                    p[0] = value

    def p_elseif_stmts(self, p):
        '''elseif_stmts :
                        | elseif_stmt elseif_stmts'''
        if len(p) > 1:
            for handler in self.handlers:
                value = handler.elseif_stmts(self, p[1], p[2])
                if p[0] is None:
                    p[0] = value

    def p_elseif_stmt(self, p):
        '''elseif_stmt : ELSEIF expr statement_list'''
        for handler in self.handlers:
            value = handler.elseif_stmt(self, p[2], p[3])
            if p[0] is None:
                p[0] = value

    def p_eostmt(self, p):
        '''eostmt : SEMI
                  | EOF
                  | END_UTL'''
        for handler in self.handlers:
            value = handler.eostmt(self, p[1])
            if p[0] is None:  # pragma: no cover
                p[0] = value

    def p_expr(self, p):
        '''expr : NOT expr
                | EXCLAMATION expr
                | expr PLUS expr
                | expr MINUS expr
                | PLUS expr %prec UMINUS
                | MINUS expr %prec UMINUS
                | expr TIMES expr
                | expr DIV expr
                | expr MODULUS expr
                | expr FILTER expr
                | literal
                | ID
                | array_ref
                | macro_call
                | paren_expr
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
                | expr DOT expr
                | expr ASSIGN expr
                | expr ASSIGNOP expr
                | expr COLON expr'''
        for handler in self.handlers:
            value = handler.expr(self, p[1], self._(p, 2), self._(p, 3))
            if p[0] is None:
                p[0] = value

    def p_for_stmt(self, p):
        '''for_stmt : FOR expr as_clause eostmt statement_list END
                    | FOR EACH expr as_clause eostmt statement_list END'''
        for handler in self.handlers:
            if len(p) == 8:
                # account for EACH
                value = handler.for_stmt(self, p[3], p[4], p[6])
            else:
                value = handler.for_stmt(self, p[2], p[3], p[5])
            if p[0] is None:
                p[0] = value

    def p_if_stmt(self, p):
        '''if_stmt : IF expr eostmt statement_list elseif_stmts else_stmt END
                   | IF expr eostmt elseif_stmts else_stmt END'''
        for handler in self.handlers:
            if len(p) == 8:
                value = handler.if_stmt(self, p[2], p[4], p[5], p[6])
            else:
                value = handler.if_stmt(self, p[2], None, p[4], p[5])
            if p[0] is None:
                p[0] = value

    def p_include_stmt(self, p):
        '''include_stmt : INCLUDE expr'''
        for handler in self.handlers:
            value = handler.include_stmt(self, p[2])
            if p[0] is None:
                p[0] = value

    def p_literal(self, p):
        '''literal : NUMBER
                   | STRING
                   | FALSE
                   | TRUE
                   | NULL
                   | array_literal'''
        for handler in self.handlers:
            value = handler.literal(self, p[1])
            if p[0] is None:
                p[0] = value

    def p_macro_call(self, p):
        '''macro_call : expr LPAREN RPAREN
                      | expr LPAREN arg_list RPAREN'''
        for handler in self.handlers:
            if len(p) == 4:
                value = handler.macro_call(self, p[1], None)
            else:
                value = handler.macro_call(self, p[1], p[3])
            if p[0] is None:
                p[0] = value

    def p_macro_decl(self, p):
        '''macro_decl : MACRO dotted_id
                      | MACRO dotted_id LPAREN param_list RPAREN
        '''
        for handler in self.handlers:
            value = handler.macro_decl(self, p[2], self._(p, 4))
            if p[0] is None:
                p[0] = value

    def p_macro_defn(self, p):
        '''macro_defn : macro_decl eostmt statement_list END
                      | macro_decl eostmt END'''
        for handler in self.handlers:
            value = handler.macro_defn(self, p[1], p[3] if p[3] != 'end' else None)
            if p[0] is None:
                p[0] = value

    def p_param_decl(self, p):
        '''param_decl : ID
                      | ID ASSIGN expr'''
        for handler in self.handlers:
            value = handler.param_decl(self, p[1], self._(p, 3))
            if p[0] is None:
                p[0] = value

    def p_param_list(self, p):
        '''param_list :
                      | param_decl COMMA param_list
                      | param_decl '''
        if len(p) > 1:
            for handler in self.handlers:
                value = handler.param_list(self, p[1], self._(p, 3))
                if p[0] is None:
                    p[0] = value

    def p_paren_expr(self, p):
        '''paren_expr : LPAREN expr RPAREN'''
        if p[2] is not None:
            for handler in self.handlers:
                value = handler.paren_expr(self, p[2])
                if p[0] is None:
                    p[0] = value

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expr
                       | RETURN'''
        for handler in self.handlers:
            value = handler.return_stmt(self, self._(p, 2))
            if p[0] is None:
                p[0] = value

    def p_while_stmt(self, p):
        '''while_stmt : WHILE expr statement_list END'''
        for handler in self.handlers:
            value = handler.while_stmt(self, p[2], p[3])
            if p[0] is None:
                p[0] = value
