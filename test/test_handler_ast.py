#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`handler_ast`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import os

import utl_parse_test
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.utl_yacc import UTLParser
from utl_lib.ast_node import ASTNode


class UTLParseHandlerASTTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST`."""
        handler = UTLParseHandlerAST()
        utldoc = handler.utldoc(ASTNode('statement_list', False, {}, []))
        self.assertEqual(utldoc, ASTNode('statement_list', False, {}, []))

    def assertJSONFileMatches(self, utl_filename, json_filename, output_filename=""):  # pylint: disable=W0221
        """Wrapper function that supplies correct handler to
        :py:meth:`utl_lib.utl_parse_test.assertJSONFileMatches`, and optionally writes the AST
        to a file for later inspection.

        """
        if output_filename:
            parser = UTLParser([UTLParseHandlerAST()])
            with open(os.path.join(self.data_dir, utl_filename), 'r') as utlin:
                with open(os.path.join(self.data_dir, output_filename), "w") as jsonout:
                    jsonout.write(parser.parse(utlin.read()).json_format())
        super().assertJSONFileMatches(UTLParseHandlerAST(),
                                      utl_filename, json_filename)

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
        self.assertJSONFileMatches('if_stmts.utl', 'if_stmts_ast.json')


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
