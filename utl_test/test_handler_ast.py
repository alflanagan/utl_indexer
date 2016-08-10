#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`handler_ast`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import os

from utl_test import utl_parse_test
from utl_lib.handler_ast import UTLParseHandlerAST, UTLParseError
from utl_lib.utl_yacc import UTLParser
from utl_lib.ast_node import ASTNode


class UTLParseHandlerASTTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST`."""
        handler = UTLParseHandlerAST()
        parser = UTLParser([handler])
        utldoc = handler.utldoc(parser, ASTNode('statement_list', {}, []))
        self.assertEqual(utldoc, ASTNode('statement_list', {}, []))

    # pylint: disable=W0221
    def assertJSONFileMatches(self, utl_filename, json_filename, output_filename=""):
        """Wrapper function that supplies correct handler to
        :py:meth:`utl_lib.utl_parse_test.assertJSONFileMatches`, and optionally writes the AST
        to a file for later inspection.

        :param str utl_filename: A UTL file to be processed using `handler`.

        :param str json_filename: A JSON file of expected results.

        :param str output_filename: Optional. If present, AST is written to this file in JSON
            format. Mostly useful for debugging.

        """
        if output_filename:
            parser = UTLParser([UTLParseHandlerAST()])
            with open(os.path.join(self.data_dir, utl_filename), 'r') as utlin:
                with open(os.path.join(self.data_dir, output_filename), "w") as jsonout:
                    jsonout.write(parser.parse(utlin.read(), filename=utl_filename).json_format())
        super().assertJSONFileMatches(UTLParseHandlerAST(),
                                      utl_filename, json_filename)

    def test_array_literal(self):
        """Unit test :py:meth:`~utl_lib.utl_yacc.UTLParser.parse` with input of array literal expression.

        """
        self.assertJSONFileMatches('array_literal.utl', 'array_literal_ast.json')

    def test_basic_assign(self):
        """Unit test of :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST` with simple
            assignment statements.

            """
        self.assertJSONFileMatches('basic_assign.utl', 'basic_assign_ast.json')

    def test_calls(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with macro calls."""
        self.assertJSONFileMatches('calls.utl', 'calls_ast.json')

    def test_for_stmts(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with for statements."""
        self.assertJSONFileMatches('for_stmt.utl', 'for_stmt_ast.json')

    def test_if_stmts(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with if statements."""
        self.assertJSONFileMatches('if_stmts1.utl', 'if_stmts_ast1.json')
        self.assertJSONFileMatches('if_stmts2.utl', 'if_stmts_ast2.json')
        self.assertJSONFileMatches('if_stmts3.utl', 'if_stmts_ast3.json')
        self.assertJSONFileMatches('if_stmts4.utl', 'if_stmts_ast4.json')

    def test_macros(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with macro defns/calls."""
        self.assertJSONFileMatches('macros.utl', 'macros_ast.json')

    def test_includes(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with include statements."""
        self.assertJSONFileMatches('includes.utl', 'includes_ast.json')

    def test_keywords(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with keywords."""
        self.assertJSONFileMatches('keywords.utl', 'keywords_ast.json')

    def test_while(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with while statements."""
        self.assertJSONFileMatches('while.utl', 'while_ast.json')

    def test_unary_exprs(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with exprs w/unary
        operators.

        """
        self.assertJSONFileMatches('unary_exprs.utl', 'unary_exprs_ast.json')

    def test_precedence(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with exprs whose parse is
        determined by operator precedence.

        """
        self.assertJSONFileMatches('precedence.utl', 'precedence_ast.json')

    def test_empty_stmts(self):
        """Unit test :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST` with control structures
        with empty statement lists.

        """
        self.assertJSONFileMatches('empty_stmts.utl', 'empty_stmts_ast.json')

    def test_special(self):
        """A couple of method calls to exercise specific cases."""
        # call to macro_decl() with string for macro name
        handler = UTLParseHandlerAST()
        parser = UTLParser([handler])
        parser.parse("[% a = b + c %]")
        handler.macro_decl(parser, "forbin")
        handler.paren_expr(parser, None)
        self.assertRaises(UTLParseError, handler.literal, parser, 'fred')


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
