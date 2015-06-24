#!/usr/bin/env python3
"""A parse handler to construct an AST from a UTL document."""

from html import escape

from utl_lib.ast_node import ASTNode
from utl_lib.utl_parse_handler import UTLParseHandler
# pylint: disable=too-many-public-methods,missing-docstring


class UTLParseHandlerAST(UTLParseHandler):
    """A handler class for use with :py:class:`UTLParser` which has the effect of building and
    returning an abstract syntax tree (AST).

    """

    def __init__(self):
        self.documents = []

    def utldoc(self, child):
        return ASTNode('utldoc', False, {}, [child])

    def statement_list(self, child, current_node=None):
        if current_node is None:
            return ASTNode('statement_list', False, {}, [child] if child else [])
        else:
            assert current_node.symbol == 'statement_list'
            if child:
                current_node.add_child(child)
            return current_node

    def statement(self, child_or_text, is_document=False):
        if is_document:
            return ASTNode('document', True,
                           {'text': escape(child_or_text, True) if child_or_text else ''})
        if isinstance(child_or_text, str):   # is a keyword
            return ASTNode('statement', False, {}, [ASTNode(child_or_text, True)])
        return ASTNode('statement', False, {}, [child_or_text])

    def echo_stmt(self, expr):
        return ASTNode('echo', False, {}, [expr] if expr is not None else [])

    def expr(self, expr, after_op, op):  # `after_op` can be term, method_call, expr, or full_id
        if expr and op and after_op:
            if isinstance(after_op, str):  # ID
                new_id = ASTNode('id', True, {'name': after_op}, [])
                return ASTNode('expr', False, {'operator': op}, [expr, new_id])
            else:
                return ASTNode('expr', False, {"operator": op}, [expr, after_op])
        elif expr and op:  # unary OP (!)
            return ASTNode('expr', False, {"operator": op}, [expr])
        else:  # term
            return ASTNode('expr', False, {}, [after_op])

    def param_list(self, param_decl, param_list):
        if not (param_decl or param_list):
            return None
        elif param_decl and not param_list:  # first declaration processed
            return ASTNode('param_list', False, {}, [param_decl])
        else:
            param_list.add_child(param_decl)
            return param_list

    def param_decl(self, param_id, param_assign):
        if param_id:
            return ASTNode('param_decl', True, {'name': param_id})
        else:
            # take apart assignment node, replace with param_decl
            return ASTNode('param_decl', False,
                           {'name': param_assign.attributes['target']},
                           param_assign.children)

    def arg_list(self, arg, arg_list):
        if not arg_list:
            return ASTNode('arg_list', True, {}, [arg] if arg else [])
        else:
            arg_list.add_child(arg)
            return arg_list

    def arg(self, argument_or_key, value):
        if value:
            return ASTNode('arg', False, {'keyword': argument_or_key}, [value])
        else:
            return ASTNode('arg', False, {}, [argument_or_key])

    def assignment(self, target, expr, op, default):
        return ASTNode('assignment',
                       False,
                       {'target': target, 'default': default},
                       [expr] if expr else [op])

    def method_call(self, method_name, arg_list):
        # method_name is an ASTNode('id')
        my_name = method_name.attributes['symbol']
        assert isinstance(my_name, str)
        return ASTNode('method_call', False, {'name': my_name}, [arg_list] if arg_list else [])

    def full_id(self, this_id, prefix):
        if isinstance(this_id, ASTNode):
            if prefix:
                my_name = prefix + "." + this_id.attributes["symbol"]
            else:
                my_name = this_id.attributes["symbol"]
        else:
            if prefix:
                my_name = prefix + "." + this_id
            else:
                my_name = this_id
        return ASTNode("id", True, {"symbol": my_name})

    def term(self, factor, op, term):
        if not (term or op):  # factor
            return ASTNode('term', False, {}, [factor])
        else:  # term OP factor
            assert term and op and factor
            return ASTNode('term', False, {'operator': op}, [term, factor])

    def factor(self, node, keyword, paren_expr):
        if node:
            return ASTNode('factor', False, {}, [node])
        elif keyword:
            kid = ASTNode(keyword, True)
            return ASTNode('factor', False, {}, [kid])
        else:
            return ASTNode('paren_group', False, {}, [paren_expr])

    def literal(self, value):
        return ASTNode('literal', True, {'value': value}, [])

    def array_ref(self, name, expr):
        return ASTNode('array_ref', False, {'name': name}, [expr] if expr else [])

    def if_stmt(self, expr, statement_list, elseif_stmts, else_stmt):
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

    def return_stmt(self, expr):
        return ASTNode('return', False, {}, [expr] if expr else [])

    def macro_defn(self, macro_decl, statement_list):
        return ASTNode('macro-defn',
                       False,
                       {'name': macro_decl.attributes['name']},
                       [macro_decl, statement_list])

    def macro_decl(self, macro_id, param_list):
        return ASTNode('macro-decl', True, {'name': macro_id},
                       [param_list] if param_list else [])

    def for_stmt(self, expr, for_var, statement_list):
        return ASTNode('for', False,
                       {'name': for_var} if for_var else {},
                       [expr, statement_list])

    def include_stmt(self, filename):
        return ASTNode('include', True, {'file': filename})

    def abbrev_if_stmt(self, expr, statement):
        return ASTNode('if', False, {}, [expr, statement])

    def while_stmt(self, expr, statement_list):
        return ASTNode('while', False, {}, [expr, statement_list])

    def call_stmt(self, method_call):
        return ASTNode('call', False, {}, [method_call])
