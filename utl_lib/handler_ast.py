#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A parse handler to construct an AST from a UTL document.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
from utl_lib.ast_node import ASTNode
from utl_lib.utl_parse_handler import UTLParseHandler
from utl_lib.utl_lex import UTLLexer
# pylint: disable=too-many-public-methods,missing-docstring


class UTLParseHandlerAST(UTLParseHandler):
    """A handler class for use with :py:class:`UTLParser` which has the effect of building and
    returning an abstract syntax tree (AST).

    """

    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents = []

    def _dbg_print_hlpr(self, label, expr):  # pragma: no cover
        if expr is not None:
            print("*    {}: {}".format(
                label,
                expr.format().replace('\n', '\n*    ') if isinstance(expr, ASTNode) else expr))

    def _context(self, parser, other_attrs=None):
        """Returns a dictionary of info about the production context. Items in dictionary
        `other_attrs` are added to, and may override, the returned context attributes.

        """
        # TODO: sometimes, parser.lexer.lineno is 1 greater than expected, but usually not.
        # figure out why and fix.
        lm = parser.lexer.lexmatch
        attrs = {"file": parser.filename,
                 # line number is 1-based
                 "line": parser.lexer.lineno,
                 "start": lm.start(),
                 "end": lm.end(),
                 }
        if other_attrs:
            attrs.update(other_attrs)
        return attrs

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, parser, statement_list):
        return statement_list

    def statement_list(self, parser, statement=None, statement_list=None):
        assert statement is not None or statement_list is not None
        if statement_list is None:
            attrs = {"start": statement.attributes["start"],
                     "line": statement.attributes["line"],
                     # lexpos includes the final end
                     "end": parser.lexer.lexpos}
            return ASTNode('statement_list', self._context(parser, attrs), [statement])
        assert statement_list.symbol == 'statement_list'
        if statement is not None:
            statement_list.attributes["start"] = min(statement.attributes["start"],
                                                     statement_list.attributes["start"])
            statement_list.attributes["line"] = min(statement.attributes["line"],
                                                    statement_list.attributes["line"])
            statement_list.add_first_child(statement)
        return statement_list

    def statement(self, parser, statement):
        assert statement is not None
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword - break, continue, exit, etc.
                return ASTNode(statement, self._context(parser), [])
            else:
                return ASTNode('document', self._context(parser, {'text': statement}), [])
        assert isinstance(statement, ASTNode)
        return statement

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, parser, expr, statement):
        assert expr is not None
        # make statement into statement_list to match regular if
        statement_list = ASTNode('statement_list', {}, [statement])
        return ASTNode('if', self._context(parser), [expr, statement_list])

    def arg(self, parser, expr, name=None):
        assert expr is not None
        attrs = self._context(parser)
        if name is not None:
            attrs['keyword'] = name
        return ASTNode('arg', attrs, [expr])

    def arg_list(self, parser, arg, arg_list=None):
        assert arg is not None
        if arg_list is None:
            return ASTNode('arg_list', self._context(parser), [arg])
        else:
            arg_list.add_first_child(arg)
            return arg_list

    def array_elems(self, parser, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs)."""
        assert expr is not None
        if array_elems is None:
            return ASTNode('array_elems', self._context(parser), [expr])
        array_elems.add_child(expr)
        return array_elems

    def array_literal(self, parser, elements=None):
        return ASTNode('array_literal', self._context(parser), [elements] if elements else [])

    def array_ref(self, parser, variable, index):
        assert variable is not None
        assert index is not None
        # parser lexical context is for index, set start from variable instead
        # end doesn't include "]" character, so add 1
        attrs = {"start": variable.attributes["start"],
                 "line": variable.attributes["line"],
                 "end": index.attributes["end"] + 1}
        return ASTNode('array_ref', self._context(parser, attrs), [variable, index])

    def as_clause(self, parser, var1, var2=None):
        # We handle target variables as attributes of for node. So, we just need to return the
        # names.
        return (var1, var2, )

    def call_stmt(self, parser, macro_call):
        return ASTNode('call', self._context(parser), [macro_call])

    def default_assignment(self, parser, assignment):
        return ASTNode('default', self._context(parser), [assignment])

    def dotted_id(self, parser, this_id, id_suffix=None):
        if id_suffix is not None:
            id_suffix.attributes['symbol'] = this_id + '.' + id_suffix.attributes['symbol']
            return id_suffix
        attrs = self._context(parser, {'symbol': this_id})
        return ASTNode('id', attrs, [])

    def echo_stmt(self, parser, expr):
        return ASTNode('echo', self._context(parser), [expr] if expr is not None else [])

    def else_stmt(self, parser, statement_list):
        return ASTNode('else', self._context(parser),
                       [statement_list] if statement_list is not None else [])

    def elseif_stmts(self, parser, elseif_stmt, elseif_stmts=None):
        assert elseif_stmt is not None
        if elseif_stmts is not None:
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', self._context(parser), [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, parser, expr, statement_list=None):
        assert expr is not None
        if statement_list is None:
            statement_list = ASTNode('statement_list', self._context(parser), [])
        return ASTNode('elseif', self._context(parser), [expr, statement_list])

    def expr(self, parser, first, second=None, third=None):
        assert first is not None
        # first possible values:
        #    NOT|EXCLAMATION|PLUS|MINUS|ID|literal|array_ref|macro_call|paren_expr|expr
        if isinstance(first, str):
            if second is not None:
                return ASTNode('expr', self._context(parser, {'operator': first.lower()}), [second])
            else:
                return ASTNode("id", self._context(parser, {"symbol": first}), [])
        elif second is None:
            return first

        # special case: reduce dotted ID expressions
        if second == '.':
            if first.symbol == 'id' and third.symbol == 'id':
                parts = [first.attributes["symbol"], third.attributes["symbol"]]
                attrs = {"symbol": ".".join(parts)}
                # lexer context here is for 2nd symbol, so override "start" to include first symbol
                attrs["start"] = first.attributes["start"]
                return ASTNode("id", self._context(parser, attrs), [])

        # if we got this far, it's a binary op
        assert third is not None
        assert isinstance(second, str)
        return ASTNode('expr', self._context(parser, {'operator': second.lower()}), [first, third])

    def for_stmt(self, parser, expr, as_clause=None, statement_list=None):
        assert expr is not None
        attrs = {}
        if as_clause is not None:
            attrs["name1"] = as_clause[0]
            if as_clause[1] is not None:
                attrs["name2"] = as_clause[1]
        return ASTNode('for', self._context(parser, attrs),
                       [expr, statement_list] if statement_list else [expr])

    def if_stmt(self, parser, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        assert expr is not None
        # so 'if' node always looks same, create empty nodes for missing ones
        attrs = self._context(parser)
        if statement_list is None:
            statement_list = ASTNode("statement_list", attrs, [])
        if elseif_stmts is None:
            elseif_stmts = ASTNode("elseif_stmts", attrs, [])
        if else_stmt is None:
            else_stmt = ASTNode("else", attrs, [])
        kids = [expr, statement_list, elseif_stmts, else_stmt]
        return ASTNode('if', attrs, kids)

    def include_stmt(self, parser, filename):
        return ASTNode('include', self._context(parser, {'file': filename}), [])

    def literal(self, parser, literal):
        return ASTNode("literal", self._context(parser, {"value": literal}), [])

    def macro_call(self, parser, macro_expr, arg_list=None):
        if arg_list is None:
            arg_list = ASTNode("arg_list", self._context(parser), [])
        code = parser.lexer.lexdata
        # parser lexer context may not include entire macro_expr, reset start
        start = macro_expr.attributes["start"]
        attrs = {"start": start,
                 # everything before opening (; may be ID, may be expr
                 "macro_expr": code[start:macro_expr.attributes["end"]]
                 }
        return ASTNode("macro_call", self._context(parser, attrs), [macro_expr, arg_list])

    def macro_decl(self, parser, macro_name, param_list=None):
        # if macro_name is a string, the production was
        if isinstance(macro_name, ASTNode):
            assert macro_name.symbol == 'id'
            macro_name = macro_name.attributes['symbol']
        lex = parser.lexer
        # starting at the macro name, search backwards for the token "macro"
        macro_pos = lex.lexdata[:lex.lexmatch.start()].rfind('macro')
        return ASTNode('macro_decl', self._context(parser, {'name': macro_name,
                                                            'start': macro_pos}),
                       [param_list] if param_list else [])

    def macro_defn(self, parser, macro_decl, statement_list=None):
        return ASTNode('macro_defn',
                       # set start to the beginning of macro_decl, not statement_list
                       {"file": parser.filename,
                        "line": macro_decl.attributes["line"],
                        "start": macro_decl.attributes["start"],
                        "end": statement_list.attributes["end"]},
                       [macro_decl, statement_list] if statement_list else [macro_decl])

    def param_decl(self, parser, param_id, default_value=None):
        if not default_value:
            return ASTNode('param_decl', self._context(parser, {'name': param_id}), [])
        else:
            return ASTNode('param_decl',
                           self._context(parser, {'name': param_id,
                                                  'default': default_value}),
                           [])

    def param_list(self, parser, param_decl, param_list=None):
        assert param_decl is not None
        if not param_list:  # first declaration processed
            return ASTNode('param_list', self._context(parser), [param_decl])
        else:
            param_list.add_first_child(param_decl)
            return param_list

    def paren_expr(self, parser, expr):
        # parentheses have already determined the parse tree structure
        # so we don't need them
        if expr is not None:
            return expr

    def return_stmt(self, parser, expr=None):
        return ASTNode('return', self._context(parser), [expr] if expr else [])

    def while_stmt(self, parser, expr, statement_list=None):
        if statement_list is None:
            statement_list = ASTNode("statement_list", self._context(parser), [])
        return ASTNode('while', self._context(parser), [expr, statement_list])
