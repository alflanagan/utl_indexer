#!/usr/bin/env python3
"""A parse handler to construct a parse tree from a UTL document."""

from utl_lib.ast_node import ASTNode
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError
from utl_lib.utl_lex import UTLLexer
# pylint: disable=too-many-public-methods,missing-docstring


class UTLParseHandlerParseTree(UTLParseHandler):
    """A handler class for use with :py:class:`UTLParser` which has the effect of building and
    returning a parse tree. As opposed to an abstract syntax tree (AST), the parse tree is
    intended to closely mimic the productions of the parse that generated it.

    This makes it particularly useful for debugging the parsing process.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents = []

    def utldoc(self, statement_list):
        return ASTNode('utldoc', False, {}, [statement_list])

    def statement_list(self, statement, statement_list=None):
        if statement_list is None:
            return ASTNode('statement_list', False, {}, [statement] if statement else [])
        else:
            assert statement_list.symbol == 'statement_list'
            if statement:
                statement_list.add_child(statement)
            return statement_list

    def statement(self, statement):
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword
                return ASTNode('statement', False, {}, [ASTNode(statement, True)])
            else:
                return ASTNode('statement', False, {},
                               [ASTNode('document', True, {'text': statement}, [])])
        if statement:  # ignore null statements
            return ASTNode('statement', False, {}, [statement] if statement else [])

    def echo_stmt(self, expr):
        return ASTNode('echo', False, {}, [expr] if expr else [])

    def expr(self, start, expr1, expr2):
        if isinstance(start, str):
            if start.lower() in ('not', '!', '-', '+', ):
                start = ASTNode('unary-op', False, {'operator': start.lower()}, [expr1])
            elif start.lower() in ('false', 'true', 'null', ):
                start = ASTNode('keyword', True, {'keyword': start.lower()}, [])
            else:
                start = ASTNode('id', True, {'name': start}, [])
        elif isinstance(start, float):
            start = ASTNode('number', True, {'value': start})
        elif not isinstance(start, ASTNode):
            raise UTLParseError("Unrecognized start to an expr: {}".format(start))
        # We want the returned expression node to hide the whole expr/rexpr distinction, which is
        # implementation detail.
        # : NOT expr
        # | EXCLAMATION expr
        # | NUMBER rexpr
        # | MINUS expr %prec UMINUS
        # | PLUS expr %prec UMINUS
        # | STRING rexpr
        # | FALSE rexpr
        # | TRUE rexpr
        # | NULL rexpr
        # | ID rexpr
        # | LPAREN expr RPAREN rexpr
        # | array_literal RBRACKET rexpr'''
        if expr1 and 'operator' in expr1.attributes:
            return ASTNode('expr', False, expr1.attributes, [start] + expr1.children)
        return ASTNode('expr', False, {}, [node for node in [start, expr1, expr2] if node is not None])

    def rexpr(self, operator, expr_or_arg_list, rexpr):
        # | PLUS expr
        # | MINUS expr
        # | FILTER expr
        # | TIMES expr
        # | DIV expr
        # | MODULUS expr
        # | DOUBLEBAR expr
        # | RANGE expr
        # | NEQ expr
        # | LTE expr
        # | OR expr
        # | LT expr
        # | EQ expr
        # | IS expr
        # | GT expr
        # | AND expr
        # | GTE expr
        # | DOUBLEAMP expr
        # | DOT expr
        # | ASSIGN expr
        # | ASSIGNOP expr
        # | LPAREN arg_list RPAREN rexpr
        # | LBRACKET expr RBRACKET rexpr
        return ASTNode('rexpr', False, {'operator': operator},
                       [node for node in [expr_or_arg_list, rexpr] if node is not None])

    def param_list(self, param_decl, param_list=None):
        if not (param_decl or param_list):
            return None
        if not param_list:  # first declaration processed
            return ASTNode('param_list', False, {}, [param_decl])
        else:
            param_list.add_child(param_decl)
            return param_list

    def param_decl(self, param_id, default_value=None):
        if not default_value:
            return ASTNode('param_decl', True, {'name': param_id})
        else:
            return ASTNode('param_decl', False,
                           {'name': param_id,
                            'default': default_value},
                           [])

    def arg_list(self, arg, arg_list=None):
        if not arg_list:
            return ASTNode('arg_list', True, {}, [arg] if arg else [])
        else:
            arg_list.add_child(arg)
            return arg_list

    def arg(self, expr, name=None):
        if name:
            return ASTNode('arg', False, {'keyword': name}, [expr])
        else:
            return ASTNode('arg', False, {}, [expr])

    def array_literal(self, elements=None):
        return ASTNode('array_literal', False, {}, [elements] if elements else [])

    def array_elems(self, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs)."""
        if array_elems is None:
            return ASTNode('array_elems', False, {}, [expr])
        else:
            array_elems.add_child(expr)
            return array_elems

    def key_value_elems(self, key_expr, value_expr, kv_elems=None):
        """Elements for an object-type array, with key/value pairs. `kv_elems`, if present, is
        the result of reduction of previous elements in the array expression.

        """
        new_elem = ASTNode('key_value', False, {}, [key_expr, value_expr])
        if kv_elems is None:
            return ASTNode('key_value_elems', False, {}, [new_elem])
        else:
            kv_elems.add_child(new_elem)
            return kv_elems

    def if_stmt(self, expr, statement_list, elseif_stmts=None, else_stmt=None):
        kids = [expr, statement_list]
        if elseif_stmts:
            kids.append(elseif_stmts)
        if else_stmt:
            kids.append(else_stmt)
        return ASTNode('if', False, {}, kids)

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        if elseif_stmts:
            elseif_stmts.add_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', False, {}, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, expr, statement_list):
        return ASTNode('elseif', False, {}, [expr, statement_list])

    def else_stmt(self, statement_list):
        return ASTNode('else', False, {}, [statement_list])

    def return_stmt(self, expr=None):
        return ASTNode('return', False, {}, [expr] if expr else [])

    def macro_defn(self, macro_decl, statement_list=None):
        return ASTNode('macro-defn',
                       False,
                       {'name': macro_decl.attributes['name']},
                       [macro_decl, statement_list] if statement_list else [macro_decl])

    def macro_decl(self, macro_name, param_list=None):
        if isinstance(macro_name, ASTNode):
            assert macro_name.symbol == 'id'
            macro_name = macro_name.attributes['symbol']
        return ASTNode('macro-decl', True, {'name': macro_name},
                       [param_list] if param_list else [])

    def dotted_id(self, this_id, id_prefix=None):
        if id_prefix:
            id_prefix.attributes['symbol'] += '.' + this_id
            return id_prefix
        return ASTNode('id', True, {'symbol': this_id}, [])

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        return ASTNode('for', False, {},
                       [expr, as_clause, statement_list])

    def as_clause(self, var1, var2=None):
        kids = [ASTNode('id', True, {"symbol": vname}) for vname in [var1, var2] if vname is not None]
        return ASTNode('as_clause', False, {}, kids)

    def default_assignment(self, assign_expr):
        return ASTNode('default', False, {}, [assign_expr])

    def include_stmt(self, filename):
        return ASTNode('include', True, {'file': filename})

    def abbrev_if_stmt(self, expr, statement):
        return ASTNode('if', False, {}, [expr, statement])

    def while_stmt(self, expr, statement_list):
        return ASTNode('while', False, {}, [expr, statement_list])

    def call_stmt(self, method_call):
        return ASTNode('call', False, {}, [method_call])
