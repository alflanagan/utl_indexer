#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`handler_ast`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""

from testplus import unittest_plus

from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.ast_node import ASTNode


class UTLParseHandlerASTTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST`."""
        handler = UTLParseHandlerAST()
        utldoc = handler.utldoc(ASTNode('statement_list', False, {}, []))
        self.assertEqual(utldoc,
                         ASTNode('utldoc', False, {},
                                 [ASTNode('statement_list', False, {}, [])]))


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
