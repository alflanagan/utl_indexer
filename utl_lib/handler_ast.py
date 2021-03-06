#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A parse handler to construct an AST from a UTL document.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
from typing import Union, Optional, Tuple, SupportsFloat

from utl_lib.ast_node import ASTNode
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError
from utl_lib.utl_lex import UTLLexer
# pylint: disable=too-many-public-methods,missing-docstring,too-many-arguments


class UTLParseHandlerAST(UTLParseHandler):
    """A handler class for use with :py:class:`UTLParser` which has the effect of building and
    returning an abstract syntax tree (AST).

    :param list args: plain arguments, passed on to parent constructor.

    :param dict kwargs: named arguments, passed on to parent constructor.

    """

    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.documents = []

    @staticmethod
    def _dbg_print_hlpr(label: str, expr: Union[ASTNode, str]) -> None:  # pragma: no cover
        if expr is not None:
            print("*    {}: {}".format(
                label,
                expr.format().replace('\n', '\n*    ') if isinstance(expr, ASTNode) else expr))

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, parser: UTLParser, statement_list: ASTNode) -> ASTNode:
        # the statment_list already has all relevant info
        return statement_list

    def statement_list(self, parser: UTLParser, statement: ASTNode=None,
                       statement_list: ASTNode=None) -> ASTNode:
        if statement_list is None:
            return ASTNode('statement_list', parser.context,
                           [statement] if statement is not None else [])
        assert statement_list.symbol == 'statement_list'
        if statement is not None:
            statement_list.attributes = parser.context
            statement_list.add_first_child(statement)
        return statement_list

    def statement(self, parser: UTLParser, statement: Union[str, ASTNode],
                  eostmt: str=None) -> ASTNode:
        assert statement is not None
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword - break, continue, exit, etc.
                return ASTNode(statement, parser.context, [])
            else:
                attrs = parser.context
                attrs["text"] = statement
                return ASTNode('document', attrs, [])
        assert isinstance(statement, ASTNode)
        return statement

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, parser: UTLParser, expr: ASTNode, statement: ASTNode) -> ASTNode:
        assert expr is not None
        # make statement into statement_list to match regular if
        statement_list = ASTNode('statement_list', statement.context, [statement])
        return ASTNode('if', parser.context, [expr, statement_list])

    def arg(self, parser: UTLParser, expr: ASTNode, name: str=None) -> ASTNode:
        assert expr is not None
        attrs = parser.context
        if name is not None:
            attrs['keyword'] = name
        return ASTNode('arg', attrs, [expr])

    def arg_list(self, parser: UTLParser, arg_or_list: Union[ASTNode, str],
                 arg: Union[ASTNode, str, None]=None) -> ASTNode:
        assert arg_or_list is not None
        if arg_or_list == ",":
            # use empty argument -- position may be significant
            arg_or_list = ASTNode('arg', parser.context, [])
        if arg is None:
            assert arg_or_list.symbol == 'arg'
            return ASTNode('arg_list', parser.context, [arg_or_list])
        else:
            assert arg_or_list.symbol == 'arg_list'
            if arg == ',':
                arg = ASTNode('arg', parser.context, [])
            assert arg.symbol == 'arg'
            arg_or_list.add_child(arg)
            attrs = dict(arg_or_list.attributes)
            attrs["end"] = parser.context["end"]
            arg_or_list.attributes = attrs
            return arg_or_list

    def array_elems(self, parser: UTLParser,
                    first_part: Union[str, ASTNode]=None,
                    maybe_comma: str=None,
                    rest: ASTNode=None) -> ASTNode:
        """Elements for a simple array (not key/value pairs).

        :param UTLParser parser: The parser that called this method.

        :param Union first_part: One of:

            * :py:attr:`None`
            * "expr" production (:py:class:`ASTNode`)
            * "array_elems" production (:py:class:`ASTNode`)
            * a comma (',')

        :param str maybe_comma: either "," or None

        :param ASTNode rest: either an "expr" production or :py:attr:`None`

        :note: it is an error if both ``first_part`` and ``rest`` are :py:attr:`None`.

        :return: "array_elems" node.
        :rtype: :py:class:`~utl_lib.ast_node.ASTNode`

        """
        if rest is not None and first_part is not None:
            assert isinstance(rest, ASTNode)
            assert first_part.symbol == "array_elems"
            first_part.add_child(rest)
            first_part.attributes = parser.context
            return first_part
        if first_part is not None and first_part != ',':
            if first_part.symbol == "array_elems":
                # update context for possible extra comma, etc.
                first_part.attributes = parser.context
                return first_part
            else:
                return ASTNode("array_elems", parser.context, [first_part])
        return ASTNode("array_elems", parser.context, [])

    def array_literal(self, parser: UTLParser, elements: ASTNode=None) -> ASTNode:
        attrs = parser.context
        attrs.update({'type': 'array', 'value': '[...]'})
        return ASTNode('array_literal', attrs, [elements] if elements else [])

    def array_ref(self, parser: UTLParser, variable: ASTNode, index: ASTNode) -> ASTNode:
        assert variable is not None
        assert index is not None
        return ASTNode('array_ref', parser.context, [variable, index])

    def as_clause(self, parser: UTLParser, var1: str, var2: str=None) -> Tuple[int]:
        # We handle target variables as attributes of for node. So, we just need to return the
        # names.
        return (var1, var2, )

    def call_stmt(self, parser: UTLParser, macro_call: ASTNode) -> ASTNode:
        return ASTNode('call', parser.context, [macro_call])

    def default_assignment(self, parser: UTLParser, assignment: ASTNode) -> ASTNode:
        return ASTNode('default', parser.context, [assignment])

    def dotted_id(self, parser: UTLParser, this_id: str, id_suffix: str=None) -> ASTNode:
        if id_suffix is not None:
            isinstance(id_suffix, ASTNode)
            attrs = dict(id_suffix.attributes)
            attrs['symbol'] = this_id + '.' + attrs['symbol']
            id_suffix.attributes = attrs
            return id_suffix
        attrs = parser.context
        attrs['symbol'] = this_id
        return ASTNode('id', attrs, [])

    def echo_stmt(self, parser: UTLParser, expr: Optional[ASTNode]) -> ASTNode:
        return ASTNode('echo', parser.context, [expr] if expr is not None else [])

    def else_stmt(self, parser: UTLParser, eostmt: None, statement_list: Optional[ASTNode]) -> ASTNode:
        return ASTNode('else', parser.context,
                       [statement_list] if statement_list is not None else [])

    def elseif_stmts(self, parser: UTLParser, elseif_stmt: ASTNode,
                     elseif_stmts: ASTNode=None) -> ASTNode:
        assert elseif_stmt is not None
        if elseif_stmts is not None:
            elseif_stmts.attributes = parser.context
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', elseif_stmt.attributes, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, parser: UTLParser, expr: ASTNode, eostmt: None,
                    statement_list: ASTNode=None) -> ASTNode:
        return ASTNode('elseif', parser.context,
                       [expr, statement_list] if statement_list is not None else [expr])

    def expr(self, parser: UTLParser, first: Union[ASTNode, str],
             second: Union[ASTNode, str]=None, third: ASTNode=None) -> ASTNode:
        attrs = parser.context
        if second is None:
            # literal ID array_ref macro_call paren_expr
            if hasattr(first, "symbol"):
                return first
            else:
                attrs["symbol"] = first
                return ASTNode("id", attrs, [])
        elif third is None:
            # NOT expr |  EXCLAMATION expr | PLUS expr |  MINUS expr
            attrs["operator"] = first.lower()
            return ASTNode('expr', attrs, [second])
        else:
            # expr OP expr
            attrs["operator"] = second
            return ASTNode('expr', attrs, [first, third])

    def for_stmt(self, parser: UTLParser, expr: ASTNode, as_clause: Tuple[int]=None,
                 eostmt: str=None, statement_list: ASTNode=None) -> ASTNode:
        assert expr is not None
        attrs = parser.context
        if as_clause is not None:
            attrs["name1"] = as_clause[0]
            if as_clause[1] is not None:
                attrs["name2"] = as_clause[1]
        return ASTNode('for', attrs,
                       [expr, statement_list] if statement_list else [expr])

    def if_stmt(self, parser: UTLParser, expr: ASTNode, eostmt: str=None,
                statement_list: ASTNode=None, elseif_stmts: ASTNode=None,
                else_stmt: ASTNode=None) -> ASTNode:
        assert expr is not None
        # so 'if' node always looks same, create empty nodes for missing ones
        if statement_list is None:  # pragma: no cover
            attrs = parser.context.copy()
            attrs["start"] = attrs["end"] = 0
            statement_list = ASTNode('statement_list', attrs, [])
        if elseif_stmts is None:
            attrs = parser.context.copy()
            attrs["start"] = attrs["end"] = 0
            elseif_stmts = ASTNode("elseif_stmts", attrs, [])
        if else_stmt is None:
            attrs = parser.context.copy()
            attrs["start"] = attrs["end"] = 0
            else_stmt = ASTNode("else", attrs, [])
        kids = [expr, statement_list, elseif_stmts, else_stmt]
        return ASTNode('if', parser.context, kids)

    def include_stmt(self, parser: UTLParser, filename: ASTNode) -> ASTNode:
        attrs = parser.context
        if filename.symbol == 'literal':
            attrs["file"] = filename.attributes["value"]
            return ASTNode('include', attrs, [])
        attrs["file"] = "<expr>"
        return ASTNode('include', attrs, [filename])

    def literal(self, parser: UTLParser, literal: Union[str, ASTNode]) -> ASTNode:
        if isinstance(literal, ASTNode):
            # string or numeral literal, already created for us
            return literal
        else:
            attrs = parser.context
            if literal.lower() == 'true':
                attrs.update({'type': 'boolean', 'value': True})
            elif literal.lower() == 'false':
                attrs.update({'type': 'boolean', 'value': False})
            elif literal.lower() == 'null':
                attrs.update({'type': 'null', 'value': None})
            else:
                raise UTLParseError('Unrecognized literal type/value: {}'.format(literal))
            return ASTNode("literal", attrs, [])

    def macro_call(self, parser: UTLParser, macro_expr: ASTNode,
                   arg_list: ASTNode=None) -> ASTNode:
        if arg_list is None:
            attrs = parser.context
            attrs["start"] = attrs["end"] = 0
            arg_list = ASTNode("arg_list", attrs, [])
        attrs = parser.context
        start = macro_expr.attributes["start"]
        end = macro_expr.attributes["end"]
        attrs["macro_expr"] = parser.lexer.lexdata[start:end]
        return ASTNode("macro_call", attrs, [macro_expr, arg_list])

    def macro_decl(self, parser: UTLParser, macro_name: Union[ASTNode, str],
                   param_list: ASTNode=None) -> ASTNode:
        if isinstance(macro_name, ASTNode):
            assert macro_name.symbol == 'id'
            macro_name = macro_name.attributes['symbol']

        attrs = parser.context
        attrs["name"] = macro_name
        return ASTNode('macro_decl', attrs, [param_list] if param_list else [])

    def macro_defn(self, parser: UTLParser, macro_decl: ASTNode,
                   eostmt: str, statement_list: ASTNode=None) -> ASTNode:
        return ASTNode('macro_defn',
                       parser.context,
                       [macro_decl, statement_list] if statement_list else [macro_decl])

    def number_literal(self, parser: UTLParser, literal: SupportsFloat) -> ASTNode:
        num = float(literal)
        attrs = parser.context
        attrs.update({'type': 'number', 'value': num})
        return ASTNode('literal', attrs, [])

    def param_decl(self, parser: UTLParser, param_id: str,
                   default_value: Union[str, ASTNode]=None) -> ASTNode:
        attrs = parser.context
        attrs['name'] = param_id
        return ASTNode('param_decl', attrs, [default_value] if default_value is not None else [])

    def param_list(self, parser: UTLParser, param_decl: ASTNode,
                   param_list: ASTNode=None) -> ASTNode:
        assert param_decl is not None
        if param_list is not None:
            param_list.attributes = parser.context
            param_list.add_first_child(param_decl)
            return param_list
        else:
            return ASTNode('param_list', parser.context, [param_decl])

    def paren_expr(self, parser: UTLParser, expr: Optional[ASTNode]) -> Union[ASTNode, None]:
        # parentheses have already determined the parse tree structure
        # so we don't need them
        return expr

    def return_stmt(self, parser: UTLParser, expr: ASTNode=None) -> ASTNode:
        return ASTNode('return', parser.context, [expr] if expr else [])

    def string_literal(self, parser: UTLParser, literal: str) -> ASTNode:
        assert isinstance(literal, str)
        attrs = parser.context
        attrs.update({'type': 'string', 'value': literal})
        return ASTNode('literal', attrs, [])

    def while_stmt(self, parser: UTLParser, expr: ASTNode, eostmt: ASTNode,
                   statement_list: ASTNode=None) -> ASTNode:
        return ASTNode('while', parser.context, [expr, statement_list])
