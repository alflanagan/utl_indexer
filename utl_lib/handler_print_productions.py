#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A UTLParseHandler child that does nothing except print out the productions that are found.

Mostly useful for debugging.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
from utl_lib.utl_parse_handler import UTLParseHandler


# pylint: disable=unused-argument,too-many-public-methods
class UTLPrintProductionsHandler(UTLParseHandler):
    """A UTLParseHandler implementation that simply prints the productions as they occur.

    :param boolean exception_on_error: If True, a syntax error will raise a
        :py:class:`UTLParseError`, which will effectively end processing. Usually
        one wants to continue processing and report all syntax errors
        encountered.
    """
    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, exception_on_error=False, *args, **kwargs):
        super().__init__(exception_on_error, *args, **kwargs)

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, statement_list):
        print("utldoc")
        print("-" * 80)
        # it's important we return non-None value, as some productions short-circuit if they
        # have no children
        return "utldoc"

    def statement_list(self, statement=None, statement_list=None):
        print("statement_list")
        return "statement_list"

    def statement(self, statement):
        print("statement")
        return "statement"

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        print("abbrev_if_stmt")
        return "abbrev_if_stmt"

    def arg(self, expr, name=None):
        print("arg")
        return "arg"

    def arg_list(self, arg, arg_list=None):
        print("arg_list")
        return "arg_list"

    def array_elems(self, expr, array_elems=None):
        print("array_elems")
        return "array_elems"

    def array_literal(self, elements=None):
        print("array_literal")
        return "array_literal"

    def array_ref(self, variable, index):
        print("array_ref")
        return "array_ref"

    def as_clause(self, var1, var2=None):
        print("as_clause")
        return "as_clause"

    def call_stmt(self, macro_call):
        print("call_stmt")
        return "call_stmt"

    def default_assignment(self, assignment):
        print("default_assignment")
        return "default_assignment"

    def dotted_id(self, this_id, id_suffix=None):
        print("dotted_id")
        return "dotted_id"

    def echo_stmt(self, expr):
        print("echo_stmt")
        return "echo_stmt"

    def else_stmt(self, statement_list):
        print("else_stmt")
        return "else_stmt"

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        print("elseif_stmts")
        return "elseif_stmts"

    def elseif_stmt(self, expr, statement_list):
        print("elseif_stmt")
        return "elseif_stmt"

    def eostmt(self, marker_text):
        print("eostmt")
        return "eostmt"

    def expr(self, first, second=None, third=None):
        print("expr")
        return "expr"

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        print("for")
        return "for"

    def if_stmt(self, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        print("if")
        return "if"

    def include_stmt(self, filename):
        print("include")
        return "include"

    def literal(self, literal):
        print("literal")
        return "literal"

    def macro_call(self, macro_expr, arg_list=None):
        print("macro_call")
        return "macro_call"

    def macro_decl(self, macro_name, param_list=None):
        print("macro_decl")
        return "macro_decl"

    def macro_defn(self, macro_decl, statement_list=None):
        print("macro_defn")
        return "macro_defn"

    def param_decl(self, param_id, default_value=None):
        print("param_decl")
        return "param_decl"

    def param_list(self, param_decl, param_list=None):
        print("param_list")
        return "param_list"

    def paren_expr(self, expr):
        print("paren_expr")
        return "paren_expr"

    def return_stmt(self, expr=None):
        print("return_stmt")
        return "return_stmt"

    def while_stmt(self, expr, statement_list):
        print("while_stmt")
        return "while_stmt"
