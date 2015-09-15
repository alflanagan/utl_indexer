#!/usr/bin/env python3
"""A parse handler to construct an AST from a UTL document."""

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

    def statement_list(self, statement, statement_list=None):
        if statement_list is None:
            return ASTNode('statement_list', False, {}, [statement] if statement else [])
        else:
            assert statement_list.symbol == 'statement_list'
            if statement:
                statement_list.add_first_child(statement)
            return statement_list

    def statement(self, statement):
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword
                return ASTNode(statement, True, {}, [])
            else:
                return ASTNode('document', True, {'text': statement}, [])
        if statement:  # ignore null statements
            assert isinstance(statement, ASTNode)
            return statement

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        statement_list = ASTNode('statement_list', False, {}, [statement])
        return ASTNode('if', False, {}, [expr, statement_list])

    def arg(self, expr, name=None):
        if name:
            return ASTNode('arg', False, {'keyword': name}, [expr])
        else:
            return ASTNode('arg', False, {}, [expr])

    def arg_list(self, arg, arg_list=None):
        if not arg_list:
            return ASTNode('arg_list', True, {}, [arg] if arg else [])
        else:
            arg_list.add_first_child(arg)
            return arg_list

    def array_elems(self, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs)."""
        if array_elems is None:
            return ASTNode('array_elems', False, {}, [expr])
        else:
            array_elems.add_child(expr)
            return array_elems

    def array_literal(self, elements=None):
        return ASTNode('array_literal', False, {}, [elements] if elements else [])

    def array_ref(self, variable, index):
        pass

    def as_clause(self, var1, var2=None):
        # We handle target variables as attributes of for node. So, we just need to return the
        # names.
        return (var1, var2, )

    def call_stmt(self, macro_call):
        return ASTNode('call', False, {}, [macro_call])

    def default_assignment(self, assignment):
        return ASTNode('default', False, {}, [assignment])

    def dotted_id(self, this_id, id_suffix=None):
        if id_suffix:
            id_suffix.attributes['symbol'] = this_id + '.' + id_suffix.attributes['symbol']
            return id_suffix
        return ASTNode('id', True, {'symbol': this_id}, [])

    def echo_stmt(self, expr):
        return ASTNode('echo', False, {}, [expr] if expr else [])

    def else_stmt(self, statement_list):
        return ASTNode('else', False, {}, [statement_list])

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        if elseif_stmts:
            elseif_stmts.add_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', False, {}, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, expr, statement_list):
        return ASTNode('elseif', False, {}, [expr, statement_list])

    def expr(self, first, second, third):

        if isinstance(first, str) and first.lower() in ('not', '!', '-', '+', ):
            return ASTNode('unary-op', False, {'operator': first.lower()}, [second])

        # LPAREN expr RPAREN rexpr
        if first == '(':
            # here, LPAREN is NOT a macro call
            # and we don't need the () in the AST
            if not third:
                return second
            # merge the nodes under rexpr operator
            return ASTNode("operator", False, {"symbol": third.attributes["symbol"]},
                           [second] + third.children)

        # literal rexpr | dotted_id rexpr
        if first.symbol in ['literal', 'id']:
            if not second:
                return first
            if second.symbol in ("(", "[", ):
                return ASTNode("operator", {"symbol": third.attributes["symbol"]},
                               [ASTNode("operator", {"symbol": second.symbol},
                                        [first] + second.children)] + third.children)
            # start is LHS, expr1 child is RHS, merge under rexpr operator
            assert third is None
            return ASTNode("operator", False, {"symbol": second.attributes["symbol"]},
                           [first] + second.children)
        # uh, oops
        raise UTLParseError("expr handler got unexpected operator: {}".format(first))

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        attrs = {}
        if as_clause is not None:
            attrs["name1"] = as_clause[0]
            if as_clause[1] is not None:
                attrs["name2"] = as_clause[1]
        return ASTNode('for', False, attrs,
                       [expr, statement_list] if statement_list else [expr])

    def if_stmt(self, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
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

    def macro_call(self, macro_epxr, arg_list=None):
        if arg_list is None:
            arg_list = ASTNode("arg_list", True, {}, [])
        return ASTNode("macro_call", False, {}, [arg_list])

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
