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
    #-------------------------------------------------------------------------------------------
    # admin stuff
    #-------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #-------------------------------------------------------------------------------------------
    # top-level productions
    #-------------------------------------------------------------------------------------------
    def utldoc(self, statement_list):
        return ASTNode('utldoc', False, {}, [statement_list])

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
            if statement in UTLLexer.reserved:  # is a keyword (break, return, continue)
                return ASTNode('statement', False, {}, [ASTNode(statement, True)])
            else:
                return ASTNode('statement', False, {},
                               [ASTNode('document', True, {'text': statement}, [])])
        return ASTNode('statement', False, {}, [statement] if statement else [])
    #-------------------------------------------------------------------------------------------
    # regular productions
    #-------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        return ASTNode('abbrev_if_stmt', False, {}, [expr, statement])

    def arg(self, expr, name=None):
        return ASTNode('arg', False, {'name': name}, [expr])

    def arg_list(self, arg, arg_list=None):
        if arg_list is None:
            return ASTNode('arg_list', False, {}, [arg])
        else:
            arg_list.add_child(arg)
            return arg_list

    def array_elems(self, expr, array_elems=None):
        if array_elems is not None:
            isinstance(array_elems, ASTNode)
            array_elems.add_child(expr)
            return array_elems
        elif expr is not None:
            return ASTNode('array_elems', False, {}, [expr])
        else:
            return ASTNode('array_elems', True, {}, [])

    def array_literal(self, elements=None):
        return ASTNode('array_literal', False, {},
                       [elements] if elements is not None else [])

    def array_ref(self, variable, index):
        # should we perhpas treat this as expr with operator '['?
        return ASTNode('array_ref', False, {}, [variable, index])

    def as_clause(self, var1, var2=None):
        kids = [ASTNode('id', True, {"symbol": vname}) for vname in [var1, var2] if vname is not None]
        return ASTNode('as_clause', False, {}, kids)

    def call_stmt(self, macro_call):
        return ASTNode('call_stmt', False, {}, [macro_call])

    def default_assignment(self, assignment):
        return ASTNode('default_assignment', False, {}, [assignment])

    def dotted_id(self, this_id, id_suffix=None):
        if id_suffix:
            id_suffix.attributes['symbol'] = this_id + '.' + id_suffix.attributes['symbol']
            return id_suffix
        return ASTNode('id', True, {'symbol': this_id}, [])

    def echo_stmt(self, expr):
        return ASTNode('echo', False, {}, [expr] if expr else [])

    def else_stmt(self, statement_list):
        return ASTNode('else_stmt', False, {}, [statement_list])

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        if elseif_stmts:
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', False, {}, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, expr, statement_list):
        return ASTNode('elseif_stmt', False, {}, [expr, statement_list])

    def expr(self, first, second, third):
        """An expression production

            first is: not|!|expr|literal|ID|LBRACKET|LPAREN

            second is: expr|PLUS|MINUS|TIMES|DIV|MODULUS|FILTER|DOUBLEBAR|RANGE|NEQ|LTE|OR|LT|EQ|IS|
                       GT|AND|GTE|DOUBLEAMP|DOT|ASSIGN|ASSIGNOP|COMMA|COLON

            third is: expr|RBRACKET|RPAREN

        """
        if third is not None:
            # = isn't exactly an operator, but...
            if second in UTLLexer.operator_list or second == '=':
                return ASTNode('expr', False, {'operator': second}, [first, third])
            elif (first, third) in [("(", ")"), ("[", "]")]:
                return ASTNode('expr', False, {'operator': first}, [second])
            else:
                raise UTLParseError(
                    "Got three args to expr(), can't find operator: ({}, {}, {})"
                    "".format(first, second, third))
        elif second is not None:
            assert third is None
            # first is a unary operator
            return ASTNode('expr', False, {'operator': first}, [second])
        else:
            assert second is None and third is None
            # first is a literal or an ID or an array reference
            if isinstance(first, ASTNode):  # literal or array ref
                return first
                # return ASTNode('expr', False, {'operator': None}, [first])
            # ID
            return ASTNode('id', True, {'symbol': first}, [])

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        return ASTNode('for_stmt', False, {},
                       [node for node in [expr, as_clause, statement_list] if node is not None])

    def if_stmt(self, expr, statement_list, elseif_stmts=None, else_stmt=None):
        kids = [expr, statement_list]
        if elseif_stmts:
            kids.append(elseif_stmts)
        if else_stmt:
            kids.append(else_stmt)
        return ASTNode('if_stmt', False, {}, kids)

    def include_stmt(self, filename):
        return ASTNode('include_stmt', True, {}, [filename])

    def literal(self, literal):
        if isinstance(literal, str):
            if literal in ['true', 'false']:
                return ASTNode('literal', True, {'type': 'boolean', 'value': literal == 'true'})
            if literal == 'null':
                return ASTNode('literal', True, {'type': 'null', 'value': literal})
            return ASTNode('literal', True, {'type': 'string', 'value': literal}, [])
        elif isinstance(literal, float):
            return ASTNode('literal', True, {'type': 'number', 'value': literal}, [])
        else:
            return ASTNode('literal', False, {'type': 'array', 'value': ''}, [literal])

    def macro_decl(self, macro_name, param_list=None):
        return ASTNode('macro_decl', True, {},
                       [macro_name, param_list] if param_list else [macro_name])

    def macro_defn(self, macro_decl, statement_list=None):
        return ASTNode('macro_defn',
                       False,
                       {},
                       [node for node in [macro_decl, statement_list] if node is not None])

    def param_decl(self, param_id, default_value=None):
        if not default_value:
            return ASTNode('param_decl', True, {'name': param_id})
        else:
            return ASTNode('param_decl', False,
                           {'name': param_id,
                            'default': default_value})

    def param_list(self, param_decl, param_list=None):
        if param_list is not None:
            param_list.add_first_child(param_decl)
            return param_list
        else:
            return ASTNode('param_list', False, {},
                           [param_decl] if param_decl is not None else [])

    def return_stmt(self, expr=None):
        return ASTNode('return_stmt', False, {}, [expr] if expr else [])

    def unary_expr(self, unary_op, expr):
        # like middle case of expr()
        return ASTNode("unary_expr", False, {"operator": unary_op}, [expr])

    def while_stmt(self, expr, statement_list):
        return ASTNode('while_stmt', False, {}, [expr, statement_list])
