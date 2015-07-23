#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`handler_ast`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import utl_parse_test
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.ast_node import ASTNode


class UTLParseHandlerASTTestCase(utl_parse_test.TestCaseUtl):
    """Unit tests for class :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST`."""
        handler = UTLParseHandlerAST()
        utldoc = handler.utldoc(ASTNode('statement_list', False, {}, []))
        self.assertEqual(utldoc, ASTNode('statement_list', False, {}, []))

    def assertJSONFileMatches(self, utl_filename, json_filename):  # pylint: disable=W0221
        """Wrapper function that supplies correct handler to
        :py:meth:`utl_lib.utl_parse_test.assertJSONFileMatches`.

        """
        super().assertJSONFileMatches(UTLParseHandlerAST(),
                                      utl_filename, json_filename)

    def test_basic_assign(self):
        """Unit test of :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST` with simple
            assignment statements.

            """
        self.assertJSONFileMatches('basic_assign.utl', 'basic_assign_ast.json')


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
