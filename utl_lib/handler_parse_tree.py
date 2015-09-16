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
    def utldoc(self, statement_list):
        return ASTNode('utldoc', {}, [statement_list])

    def statement_list(self, statement=None, statement_list=None):
        if statement_list is None:
            return ASTNode('statement_list', {},
                           [statement] if statement is not None else [])
        else:
            if statement is not None:
                statement_list.add_first_child(statement)
            return statement_list

    def statement(self, statement):
        if isinstance(statement, str):
            if statement in UTLLexer.reserved:  # is a keyword (break, return, continue)
                return ASTNode('statement', {}, [ASTNode(statement, {}, [])])
            else:
                return ASTNode('statement', {},
                               [ASTNode('document', {'text': statement}, [])])
        elif statement is not None:
            return ASTNode('statement', {}, [statement])
        # eostmt, for one, doesn't need to appear in output
        return None

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        assert expr is not None
        return ASTNode('abbrev_if_stmt', {},
                       [expr, statement] if statement is not None else [expr])

    def arg(self, expr, name=None):
        assert expr is not None
        return ASTNode('arg', {'name': name} if name is not None else {}, [expr])

    def arg_list(self, arg, arg_list=None):
        assert arg is not None
        if arg_list is None:
            return ASTNode('arg_list', {}, [arg])
        else:
            arg_list.add_first_child(arg)
            return arg_list

    def array_elems(self, expr, array_elems=None):
        if array_elems is not None:
            if expr is not None:
                array_elems.add_child(expr)
            return array_elems
        return ASTNode('array_elems', {}, [expr] if expr is not None else [])

    def array_literal(self, elements=None):
        return ASTNode('array_literal', {},
                       [elements] if elements is not None else [])

    def array_ref(self, variable, index):
        assert variable is not None
        assert index is not None
        return ASTNode('array_ref', {}, [variable, index])

    def as_clause(self, var1, var2=None):
        assert var1 is not None
        kids = [ASTNode('id', {"symbol": var1}, [])]
        if var2 is not None:
            kids += [ASTNode('id', {'symbol': var2}, [])]
        return ASTNode('as_clause', {}, kids)

    def call_stmt(self, macro_call):
        assert macro_call is not None
        return ASTNode('call_stmt', {}, [macro_call])

    def default_assignment(self, assignment):
        assert assignment is not None
        return ASTNode('default_assignment', {}, [assignment])

    def dotted_id(self, this_id, id_suffix=None):
        assert this_id is not None
        if id_suffix:
            id_suffix.attributes['symbol'] = this_id + '.' + id_suffix.attributes['symbol']
            return id_suffix
        return ASTNode('id', {'symbol': this_id}, [])

    def echo_stmt(self, expr):
        return ASTNode('echo', {}, [expr] if expr is not None else [])

    def else_stmt(self, statement_list):
        assert statement_list is not None
        return ASTNode('else_stmt', {}, [statement_list])

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        assert elseif_stmt is not None
        if elseif_stmts is not None:
            elseif_stmts.add_first_child(elseif_stmt)
        else:
            elseif_stmts = ASTNode('elseif_stmts', {}, [elseif_stmt])
        return elseif_stmts

    def elseif_stmt(self, expr, statement_list=None):
        assert expr is not None
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('elseif_stmt', {}, [expr, statement_list])

    def expr(self, first, second=None, third=None):
        """An expression production

            first is: not|!|expr|literal|ID|LBRACKET|LPAREN|MINUS|PLUS

            second is: expr|PLUS|MINUS|TIMES|DIV|MODULUS|FILTER|DOUBLEBAR|RANGE|NEQ|LTE|OR|LT|EQ|IS|
                       GT|AND|GTE|DOUBLEAMP|DOT|ASSIGN|ASSIGNOP|COMMA|COLON

            third is: expr|RBRACKET|RPAREN

        """
        assert first is not None
        if third is not None:
            return ASTNode('expr', {'operator': second}, [first, third])
        elif second is not None:  # first is a unary operator
            return ASTNode('expr', {'operator': first}, [second])
        # first is literal, ID, array ref, macro_call
        if isinstance(first, ASTNode):
            # we could have {'operator': None} or the like as child here, to allow caller to
            # assume "expr" node has "operator" attribute, but then code still has to check
            # whether it's an actual operator
            return ASTNode('expr', {}, [first])
        # ID
        id_node = ASTNode('id', {'symbol': first}, [])
        return ASTNode('expr', {}, [id_node])

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        assert expr is not None
        if as_clause is None:
            as_clause = ASTNode('as_clause', {}, [])
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('for_stmt', {}, [expr, as_clause, statement_list])

    def if_stmt(self, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        assert expr is not None
        if statement_list is None:  # yes, oddly this is valid
            statement_list = ASTNode("statement_list", {}, [])
        kids = [expr, statement_list]
        if elseif_stmts is not None:
            kids.append(elseif_stmts)
        if else_stmt is not None:
            kids.append(else_stmt)
        return ASTNode('if_stmt', {}, kids)

    def include_stmt(self, filename):
        assert filename is not None
        return ASTNode('include_stmt', {}, [filename])

    def literal(self, literal):
        assert literal is not None
        if isinstance(literal, str):
            if literal in ['true', 'false']:
                return ASTNode('literal', {'type': 'boolean', 'value': literal == 'true'}, [])
            if literal == 'null':
                return ASTNode('literal', {'type': 'null', 'value': literal}, [])
            return ASTNode('literal', {'type': 'string', 'value': literal}, [])
        elif isinstance(literal, float):
            return ASTNode('literal', {'type': 'number', 'value': literal}, [])
        else:
            return ASTNode('literal', {'type': 'array', 'value': '[..]'}, [literal])

    def macro_call(self, macro_expr, arg_list=None):
        assert macro_expr
        return ASTNode('macro_call', {},
                       [macro_expr, arg_list] if arg_list is not None else [macro_expr])

    def macro_decl(self, macro_name, param_list=None):
        assert macro_name
        return ASTNode('macro_decl', {},
                       [macro_name, param_list] if param_list else [macro_name])

    def macro_defn(self, macro_decl, statement_list=None):
        assert macro_decl
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('macro_defn', {}, [macro_decl, statement_list])

    def param_decl(self, param_id, default_value=None):
        assert param_id
        return ASTNode('param_decl',
                       {'name': param_id} if param_id is not None else {},
                       [default_value] if default_value is not None else [])

    def param_list(self, param_decl, param_list=None):
        assert param_decl
        if param_list is not None:
            param_list.add_first_child(param_decl)
            return param_list
        else:
            return ASTNode('param_list', {}, [param_decl])

    def paren_expr(self, expr):
        assert expr
        return expr

    def return_stmt(self, expr=None):
        return ASTNode('return_stmt', {}, [expr] if expr else [])

    def while_stmt(self, expr, statement_list=None):
        assert expr is not None
        if statement_list is None:
            statement_list = ASTNode('statement_list', {}, [])
        return ASTNode('while_stmt', {}, [expr, statement_list])
