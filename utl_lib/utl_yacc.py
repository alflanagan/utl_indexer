#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import ply.yacc as yacc

from utl_lib.utl_lex import UTLLexer
from utl_lib.ast_node import ASTNode


class UTLParser(object):  # pylint: disable=too-many-public-methods
    """Represents the current state of parsing a UTL code source, and generated AST.

    AST generation is temporary measure for development. Eventually you'll define a handler
    class, which will have methods for each production to generate AST, or get information about
    specific constructs, or generate code (FORTH, anyone?). The intent is to separate the parse
    from the rest of the process, so it can be reused.

    """

    def __init__(self):
        self.parsed = False
        self.tokens = UTLLexer.tokens[:]  # make copy, so we can .remove() tokens
        # Some tokens get processed out before parsing
        self.filtered_tokens = ['COMMENT', 'START_UTL', 'END_UTL']
        for tok in self.filtered_tokens:
            self.tokens.remove(tok)
        self.parser = yacc.yacc(module=self)
        self.lexer = UTLLexer()
        self.documents = []

    precedence = (
        ('left', 'PLUS', 'MINUS', 'OP'),
        ('left', 'TIMES', 'DIV', 'MODULUS'),
    )

    def _filtered_token(self):
        tok = self.lexer.token()
        # since DOCUMENT can occur virtually anywhere, it doesn't fit into the parse tree well
        while tok and tok.type in self.filtered_tokens:
            # if tok.type == 'DOCUMENT':
                # self.documents.append(tok)
            tok = self.lexer.token()
        return tok

    def parse(self, input_text=None, debug=False, tracking=False):
        """Parses the code in `input_text`, returns result.

        lexer defaults to the `lexer` of a new instance of
        :py:class:`~utl_lib.utl_lex.UTLLexer`.

        """
        return self.parser.parse(input=input_text, lexer=self.lexer, debug=debug,
                                 tracking=tracking, tokenfunc=self._filtered_token)

    def p_utldoc(self, p):  # pylint: disable=unused-argument
        '''utldoc : statement_list'''
        self.parsed = True
        p[0] = ASTNode('utldoc', False, {}, [p[1]])

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                          | statement'''
        if len(p) == 2:
            p[0] = ASTNode('statement_list', False, {}, [p[1]])
        else:
            assert p[1].symbol == 'statement_list'
            p[1].add_child(p[2])
            p[0] = p[1]

    def p_statement(self, p):
        '''statement : expr SEMI
                     | assignment SEMI
                     | simple_if_stmt SEMI
                     | abbrev_if_stmt SEMI
                     | if_else_stmt SEMI
                     | return_stmt SEMI
                     | macro_defn SEMI
                     | echo_stmt SEMI
                     | for_stmt SEMI
                     | include_stmt SEMI
                     | BREAK SEMI
                     | CONTINUE SEMI
                     | DOCUMENT'''
        if len(p) == 2:
            p[0] = ASTNode('document', True, {'text': p[1]})
        elif isinstance(p[1], str):
            if p[1].lower() == 'continue':
                p[0] = ASTNode('statement', False, {}, [ASTNode('continue', True)])
            elif p[1].lower() == 'break':
                p[0] = ASTNode('statement', False, {}, [ASTNode('break', True)])
        else:
            p[0] = ASTNode('statement', False, {}, [p[1]])

    def p_echo_stmt(self, p):
        '''echo_stmt : ECHO
                     | ECHO expr'''
        p[0] = ASTNode('echo', False, {}, [] if len(p) == 2 else[p[2]])

    def p_expr(self, p):
        '''expr : expr PLUS term
                | expr MINUS term
                | term
                | expr FILTER method_call
                | expr FILTER ID
                | expr OP expr

                '''
        if len(p) == 4:
            assert p[2]
            if isinstance(p[3], str):  # ID
                new_id = ASTNode('id', True, {'name': p[3]}, [])
                p[0] = ASTNode('expr', False, {'operator': p[2]}, [p[1], new_id])
            else:
                p[0] = ASTNode('expr', False, {"operator": p[2]}, [p[1], p[3]])
        else:
            p[0] = ASTNode('expr', False, {}, p[1:])

    def p_param_list(self, p):
        '''param_list :
                      | param_list COMMA param_decl
                      | param_decl '''
        if len(p) == 1:
            pass
        elif len(p) == 2:
            p[0] = ASTNode('param_list', False, {}, [p[1]])
        else:
            assert p[1].symbol == 'param_list'
            assert p[3].symbol == 'param_decl'
            p[1].add_child(p[3])
            p[0] = p[1]

    def p_param_decl(self, p):
        '''param_decl : ID
                      | assignment'''
        if isinstance(p[1], str):
            p[0] = ASTNode('param_decl', True, {'name': p[1]})
        else:
            assert p[1].symbol == 'assignment'
            p[0] = ASTNode('param_decl', False, {'name': p[1].attributes['target']},
                           p[1].children)

    def p_arg_list(self, p):
        '''arg_list :
                    | arg
                    | arg_list COMMA arg'''
        if len(p) == 1:
            p[0] = ASTNode('arg_list', True, {}, [])
        elif len(p) == 2:
            p[0] = ASTNode('arg_list', False, {}, [p[1]])
        else:
            assert p[1].symbol == "arg_list"
            p[1].add_child(p[3])
            p[0] = p[1]

    def p_arg(self, p):
        '''arg : expr
               | STRING COLON expr'''
        if len(p) == 4:
            assert p[2] == ':' and p[1]
            p[0] = ASTNode('arg', False, {'keyword': p[1]}, [p[3]])
        else:
            p[0] = ASTNode('arg', False, {}, [p[1]])

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expr
                      | ID ASSIGNOP expr'''
        p[0] = ASTNode('assignment', False, {'target': p[1]}, [p[3]])

    def p_method_call(self, p):
        '''method_call : ID LPAREN arg_list RPAREN'''
        assert p[1]
        p[0] = ASTNode('method_call', False, {'name': p[1]}, [p[3]])

    def p_term(self, p):
        '''term : term TIMES factor
                | term DIV factor
                | term MODULUS factor
                | factor'''
        if len(p) == 2:
            p[0] = ASTNode('term', False, {}, [p[1]])
        else:
            assert p[2]
            p[0] = ASTNode('term', False, {'operator': p[2]}, [p[1], p[3]])

    def p_factor(self, p):
        '''factor : literal
                  | id_ref
                  | FALSE
                  | TRUE
                  | NULL
                  | LPAREN expr RPAREN
                  | method_call'''
        # odd to have string here, but "5" can auto-convert to 5.0, so it's legal
        if len(p) == 2:
            p[0] = ASTNode('factor', False, {}, [p[1]])
        else:
            assert p[1] == '(' and p[3] == ')'
            p[0] = ASTNode('paren_group', False, {}, [p[2]])

    def p_literal(self, p):
        '''literal : NUMBER
                   | STRING'''
        assert p[1] is not None
        p[0] = ASTNode('literal', True, {'value': p[1]}, [])

    # exists because it's easier than trying to identify ID in p_factor()
    def p_id_ref(self, p):
        '''id_ref : ID LBRACKET expr RBRACKET
                  | ID'''
        if len(p) == 2:
            assert p[1]
            p[0] = ASTNode('identifier', True, {'name': p[1]})
        else:
            assert p[2] == "[" and p[4] == "]"
            p[0] = ASTNode('array-ref', False, {'name': p[1]}, [p[3]])

    def p_simple_if_stmt(self, p):
        '''simple_if_stmt : IF LPAREN expr RPAREN SEMI statement_list END'''
        p[0] = ASTNode('if', False, {}, [p[3], p[6]])

    def p_if_else_stmt(self, p):
        '''if_else_stmt : IF LPAREN expr RPAREN SEMI statement_list  ELSE SEMI statement_list END'''
        p[0] = ASTNode('if', False, {}, [p[3], p[6], p[9]])

    def p_return_stmt(self, p):
        '''return_stmt : RETURN expr'''
        assert p[2].symbol == 'expr'
        p[0] = ASTNode('return', False, {}, [p[2]])

    def p_macro_defn(self, p):
        '''macro_defn : macro_decl SEMI statement_list END'''
        p[0] = ASTNode('macro-defn',
                       False,
                       {'name': p[1].attributes['name']},
                       [p[1], p[3]])

    def p_macro_decl(self, p):
        '''macro_decl : MACRO ID
                      | MACRO ID LPAREN param_list RPAREN
        '''
        p[0] = ASTNode('macro-decl', True, {'name': p[2]},
                       # don't add param_list if it's empty
                       [] if len(p) < 5 or not p[4] else [p[4]])

    def p_for_stmt(self, p):
        '''for_stmt : FOR expr AS ID SEMI statement_list END
                    | FOR expr SEMI statement_list END
                    | FOR EACH expr AS ID SEMI statement_list END
                    | FOR EACH expr SEMI statement_list END'''
        if isinstance(p[2], str) and p[2].lower() == 'each':
            if isinstance(p[4], str) and p[4].lower() == 'as':
                p[0] = ASTNode('for', False, {'name': p[5]}, [p[3], p[7]])
            else:
                p[0] = ASTNode('for', False, {'name': None}, [p[3], p[5]])
        else:
            if isinstance(p[3], str) and p[3].lower() == 'as':
                p[0] = ASTNode('for', False, {'name': p[4]}, [p[2], p[6]])
            else:
                p[0] = ASTNode('for', False, {'name': None}, [p[2], p[4]])


    def p_include_stmt(self, p):
        '''include_stmt : INCLUDE STRING'''
        p[0] = ASTNode('include', True, {'file': p[2]})

    def p_abbrev_if_stmt(self, p):
        '''abbrev_if_stmt : IF expr THEN statement'''
        p[0] = ASTNode('if', False, {}, [p[2], p[4]])

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
