#!/usr/bin/env python3
"""A parse handler to construct a parse tree from a UTL document."""

from utl_lib.ast_node import ASTNode
from utl_lib.utl_parse_handler import UTLParseHandler
from utl_lib.utl_lex import UTLLexer
# pylint: disable=too-many-public-methods,missing-docstring


class UTLParseHandlerParseTree(UTLParseHandler):
    """A handler class for use with :py:class:`UTLParser` which has the effect of building and
    returning a parse tree. As opposed to an abstract syntax tree (AST), the parse tree is
    intended to closely mimic the productions of the parse that generated it.

    This makes it particularly useful for debugging the parsing process.

    """
    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, parser, statement_list):
        # statement_list is None if document completely empty
        return ASTNode('utldoc', parser.context,
                       [statement_list] if statement_list is not None else [])

    def statement_list(self, parser, statement=None, statement_list=None):
        if statement_list is None:
            return ASTNode('statement_list', parser.context,
                           [statement] if statement is not None else [])
        else:
            if statement is not None:
                # yes, this seems weird. but UTLParser is updating context as it sees more
                # statments
                statement_list.attributes = parser.context
                statement_list.add_first_child(statement)
            return statement_list

    def statement(self, parser, statement):
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword (break, return, continue)
                return ASTNode('statement', parser.context,
                               [ASTNode(statement, parser.context, [])])
            else:
                doc_attrs = parser.context
                doc_attrs.update({'text': statement})
                return ASTNode('statement', parser.context,
                               [ASTNode('document', doc_attrs, [])])
        elif statement is not None:
            return ASTNode('statement', parser.context, [statement])
        # eostmt, for one, doesn't need to appear in output
        return None

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, parser, expr, statement):
        assert expr is not None
        return ASTNode('abbrev_if_stmt', parser.context,
                       [expr, statement] if statement is not None else [expr])

    def arg(self, parser, expr, name=None):
        assert expr is not None
        attrs = parser.context
        if name:
            attrs['name'] = name
        return ASTNode('arg', attrs, [expr])

    def arg_list(self, parser, arg, arg_list=None):
        assert arg is not None
        if arg_list is None:
            return ASTNode('arg_list', parser.context, [arg])
        else:
            arg_list.attributes = parser.context
            arg_list.add_first_child(arg)
            return arg_list

    def array_elems(self, parser, expr, array_elems=None):
        if array_elems is not None:
            if expr is not None:
                array_elems.attributes = parser.context
                array_elems.add_child(expr)
            return array_elems
        return ASTNode('array_elems', parser.context, [expr] if expr is not None else [])

    def array_literal(self, parser, elements=None):
        return ASTNode('array_literal', parser.context,
                       [elements] if elements is not None else [])

    def array_ref(self, parser, variable, index):
        assert variable is not None
        assert index is not None
        return ASTNode('array_ref', parser.context, [variable, index])

    def as_clause(self, parser, var1, var2=None):
        # TODO: Modify parser so ID has its own production, and context, so
        # we don't have to do this arithmetic here
        assert var1 is not None
        attrs = parser.context
        attrs["symbol"] = var1
        attrs["start"] = attrs["start"] + 3  # 'as '
        while parser.lexer.lexdata[attrs["start"]] in [' ', '\t', '\n']:
            attrs["start"] += 1
        attrs["end"] = attrs["start"] + len(var1)
        kids = [ASTNode('id', attrs, [])]
        if var2 is not None:
            attrs["start"] = attrs["end"] + 1
            while parser.lexer.lexdata[attrs["start"]] in [' ', '\t', '\n']:
                attrs["start"] += 1
            attrs["end"] = attrs["start"] + len(var2)
            attrs["symbol"] = var2
            kids += [ASTNode('id', attrs, [])]
        return ASTNode('as_clause', parser.context, kids)

    def call_stmt(self, parser, macro_call):
        assert macro_call is not None
        return ASTNode('call_stmt', parser.context, [macro_call])

    def default_assignment(self, parser, assignment):
        assert assignment is not None
        return ASTNode('default_assignment', parser.context, [assignment])

    def dotted_id(self, parser, this_id, id_suffix=None):
        assert this_id is not None
        attrs = parser.context
        if id_suffix:
            attrs["symbol"] = this_id + '.' + id_suffix.attributes['symbol']
            id_suffix.attributes = attrs
            return id_suffix
        attrs["symbol"] = this_id
        return ASTNode('id', attrs, [])

    def echo_stmt(self, parser, expr):
        return ASTNode('echo', parser.context, [expr] if expr is not None else [])

    def else_stmt(self, parser, statement_list):
        assert statement_list is not None
        return ASTNode('else_stmt', parser.context, [statement_list])

    def elseif_stmts(self, parser, elseif_stmt, elseif_stmts=None):
        assert elseif_stmt is not None
        if elseif_stmts is not None:
            elseif_stmts.attributes = parser.context
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', elseif_stmt.attributes, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, parser, expr, statement_list=None):
        assert expr is not None
        if statement_list is None:
            # child is dummy entry, don't give context info
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('elseif_stmt', parser.context, [expr, statement_list])

    def expr(self, parser, first, second=None, third=None):
        """An expression production

            first is: not|!|expr|literal|ID|LBRACKET|LPAREN|MINUS|PLUS

            second is: expr|PLUS|MINUS|TIMES|DIV|MODULUS|FILTER|DOUBLEBAR|RANGE|NEQ|LTE|OR|LT|EQ|IS|
                       GT|AND|GTE|DOUBLEAMP|DOT|ASSIGN|ASSIGNOP|COMMA|COLON

            third is: expr|RBRACKET|RPAREN

        """
        assert first is not None
        attrs = parser.context
        if third is not None:
            attrs["operator"] = second
            return ASTNode('expr', attrs, [first, third])
        elif second is not None:  # first is a unary operator
            attrs["operator"] = first
            return ASTNode('expr', attrs, [second])
        # first is literal, ID, array ref, macro_call
        if isinstance(first, ASTNode):
            return ASTNode('expr', parser.context, [first])
        # ID
        attrs["symbol"] = first
        id_node = ASTNode('id', attrs, [])
        return ASTNode('expr', parser.context, [id_node])

    def for_stmt(self, parser, expr, as_clause=None, statement_list=None):
        assert expr is not None
        if as_clause is None:
            as_clause = ASTNode('as_clause', {}, [])
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('for_stmt', parser.context, [expr, as_clause, statement_list])

    def if_stmt(self, parser, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        assert expr is not None
        if statement_list is None:  # yes, oddly this is valid
            statement_list = ASTNode("statement_list", {}, [])
        kids = [expr, statement_list]
        if elseif_stmts is not None:
            kids.append(elseif_stmts)
        if else_stmt is not None:
            kids.append(else_stmt)
        return ASTNode('if_stmt', parser.context, kids)

    def include_stmt(self, parser, filename):
        assert filename is not None
        return ASTNode('include_stmt', parser.context, [filename])

    def literal(self, parser, literal):
        assert literal is not None
        attrs = parser.context
        if isinstance(literal, str):
            if literal in ['true', 'false']:
                attrs.update({'type': 'boolean', 'value': literal == 'true'})
            if literal == 'null':
                attrs.update({'type': 'null', 'value': literal})
            return ASTNode('literal', attrs, [])
        elif literal.attributes.get('type') in ('number', 'string'):
            return literal  # already has everything we need.
        else:
            attrs.update({'type': 'array', 'value': '[..]'})
            return ASTNode('literal', attrs, [literal])

    def macro_call(self, parser, macro_expr, arg_list=None):
        assert macro_expr
        return ASTNode('macro_call', parser.context,
                       [macro_expr, arg_list] if arg_list is not None else [macro_expr])

    def macro_decl(self, parser, macro_name, param_list=None):
        assert macro_name
        return ASTNode('macro_decl', parser.context,
                       [macro_name, param_list] if param_list else [macro_name])

    def macro_defn(self, parser, macro_decl, statement_list=None):
        assert macro_decl
        if statement_list is None:
            attrs = parser.context
            # the end for statement_list is == end of macro_defn, but start is different
            attrs["start"] = attrs["end"]
            statement_list = ASTNode('statement_list', attrs, [])
        return ASTNode('macro_defn', parser.context, [macro_decl, statement_list])

    def number_literal(self, parser, literal):
        num = float(literal)
        attrs = parser.context
        attrs.update({'type': 'number', 'value': num})
        return ASTNode('literal', attrs, [])

    def param_decl(self, parser, param_id, default_value=None):
        assert param_id
        return ASTNode('param_decl',
                       parser.context,
                       [default_value] if default_value is not None else [])

    def param_list(self, parser, param_decl, param_list=None):
        assert param_decl
        if param_list is not None:
            param_list.attributes = parser.context
            param_list.add_first_child(param_decl)
            return param_list
        else:
            return ASTNode('param_list', parser.context, [param_decl])

    def paren_expr(self, parser, expr):
        assert expr
        expr.attributes = expr.attributes.combine(parser.context)
        return expr

    def return_stmt(self, parser, expr=None):
        return ASTNode('return_stmt', parser.context, [expr] if expr else [])

    def string_literal(self, parser, literal):
        attrs = parser.context
        attrs.update({'type': 'string', 'value': literal})
        return ASTNode('literal', attrs, [])

    def while_stmt(self, parser, expr, statement_list=None):
        assert expr is not None
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('while_stmt', parser.context, [expr, statement_list])
