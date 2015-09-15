#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A parse handler to construct an AST from a UTL document.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
from utl_lib.ast_node import ASTNode
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError
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

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, statement_list):
        return statement_list

    def statement_list(self, statement=None, statement_list=None):
        if statement_list is None:
            if statement is None:
                return None
            return ASTNode('statement_list', False, {}, [statement])
        assert statement_list.symbol == 'statement_list'
        if statement:
            statement_list.add_first_child(statement)
        return statement_list

    def statement(self, statement):
        assert statement is not None
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword - break, continue, exit, etc.
                return ASTNode(statement, True, {}, [])
            else:
                return ASTNode('document', True, {'text': statement}, [])
        assert isinstance(statement, ASTNode)
        return statement

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        assert expr is not None
        # make statement into statement_list to match regular if
        statement_list = ASTNode('statement_list', False, {}, [statement])
        return ASTNode('if', False, {}, [expr, statement_list])

    def arg(self, expr, name=None):
        assert expr is not None
        return ASTNode('arg', False, {'keyword': name} if name is not None else {}, [expr])

    def arg_list(self, arg, arg_list=None):
        assert arg is not None
        if arg_list is None:
            return ASTNode('arg_list', True, {}, [arg])
        else:
            arg_list.add_first_child(arg)
            return arg_list

    def array_elems(self, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs)."""
        assert expr is not None
        if array_elems is None:
            return ASTNode('array_elems', False, {}, [expr])
        else:
            array_elems.add_child(expr)
            return array_elems

    def array_literal(self, elements=None):
        return ASTNode('array_literal', False, {}, [elements] if elements else [])

    def array_ref(self, variable, index):
        assert variable is not None
        assert index is not None
        return ASTNode('array_ref', False, {}, [variable, index])

    def as_clause(self, var1, var2=None):
        # We handle target variables as attributes of for node. So, we just need to return the
        # names.
        return (var1, var2, )

    def call_stmt(self, macro_call):
        return ASTNode('call', False, {}, [macro_call])

    def default_assignment(self, assignment):
        return ASTNode('default', False, {}, [assignment])

    def dotted_id(self, this_id, id_suffix=None):
        if id_suffix is not None:
            id_suffix.attributes['symbol'] = this_id + '.' + id_suffix.attributes['symbol']
            return id_suffix
        return ASTNode('id', True, {'symbol': this_id}, [])

    def echo_stmt(self, expr):
        return ASTNode('echo', False, {}, [expr] if expr is not None else [])

    def else_stmt(self, statement_list):
        return ASTNode('else', False, {}, [statement_list] if statement_list is not None else [])

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        assert elseif_stmt is not None
        if elseif_stmts is not None:
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', False, {}, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, expr, statement_list):
        assert expr is not None
        if statement_list is None:
            statement_list = ASTNode('statement_list', True, {}, [])
        return ASTNode('elseif', False, {}, [expr, statement_list])

    def expr(self, first, second=None, third=None):
        assert first is not None
        # first possible values:
        #    NOT|EXCLAMATION|PLUS|MINUS|ID|literal|array_ref|macro_call|paren_expr|expr
        if isinstance(first, str):
            if second is not None:
                if first.lower() in ('not', '!', '-', '+', ):
                    return ASTNode('expr', False, {'operator': first.lower()}, [second])
                else:
                    raise UTLParseError("Unrecognized operator: '{}'".format(first))
            else:
                return ASTNode("id", True, {"symbol": first}, [])
        elif second is None:
            return first

        # special case: reduce dotted ID expressions
        if second == '.':
            if first.symbol == 'id' and third.symbol == 'id':
                parts = [first.attributes["symbol"], third.attributes["symbol"]]
                return ASTNode("id", True, {"symbol": ".".join(parts)}, [])

        # if we got this far, it's a binary op
        assert third is not None
        assert isinstance(second, str)
        return ASTNode('expr', False, {'operator': second.lower()}, [first, third])

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        assert expr is not None
        attrs = {}
        if as_clause is not None:
            attrs["name1"] = as_clause[0]
            if as_clause[1] is not None:
                attrs["name2"] = as_clause[1]
        return ASTNode('for', False, attrs,
                       [expr, statement_list] if statement_list else [expr])

    def if_stmt(self, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        assert expr is not None
        # so 'if' node always looks same, create empty nodes for missing ones
        if statement_list is None:
            statement_list = ASTNode("statement_list", True, {}, [])
        if elseif_stmts is None:
            elseif_stmts = ASTNode("elseif_stmts", True, {}, [])
        if else_stmt is None:
            else_stmt = ASTNode("else", True, {}, [])
        kids = [expr, statement_list, elseif_stmts, else_stmt]
        return ASTNode('if', False, {}, kids)

    def include_stmt(self, filename):
        return ASTNode('include', True, {'file': filename})

    def literal(self, literal):
        return ASTNode("literal", True, {"value": literal}, [])

    def macro_call(self, macro_expr, arg_list=None):
        if arg_list is None:
            arg_list = ASTNode("arg_list", True, {}, [])
        return ASTNode("macro_call", False, {}, [macro_expr, arg_list])

    def macro_decl(self, macro_name, param_list=None):
        if isinstance(macro_name, ASTNode):
            assert macro_name.symbol == 'id'
            macro_name = macro_name.attributes['symbol']
        return ASTNode('macro-decl', True, {'name': macro_name},
                       [param_list] if param_list else [])

    def macro_defn(self, macro_decl, statement_list=None):
        return ASTNode('macro-defn',
                       False,
                       {'name': macro_decl.attributes['name']},
                       [macro_decl, statement_list] if statement_list else [macro_decl])

    def param_decl(self, param_id, default_value=None):
        if not default_value:
            return ASTNode('param_decl', True, {'name': param_id})
        else:
            return ASTNode('param_decl', False,
                           {'name': param_id,
                            'default': default_value},
                           [])

    def param_list(self, param_decl, param_list=None):
        if not (param_decl or param_list):
            return None
        if not param_list:  # first declaration processed
            return ASTNode('param_list', False, {}, [param_decl])
        else:
            param_list.add_child(param_decl)
            return param_list

    def paren_expr(self, expr):
        # parentheses have already determined the parse tree structure
        # so we don't need them
        if expr is not None:
            return expr

    def return_stmt(self, expr=None):
        return ASTNode('return', False, {}, [expr] if expr else [])

    def while_stmt(self, expr, statement_list):
        return ASTNode('while', False, {}, [expr, statement_list])
